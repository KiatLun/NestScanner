from app.graph.onboarding.onboardingDownloadResolver import (
    resolveOnboardingDownload,
)

from app.services.echoforge.model.modelListManager import (
    addModelListEntry,
    removeModelListEntry,
)

from app.services.echoforge.model.modelInfoBuilder import (
    buildModelInfo,
    writeModelInfo,
)

from app.services.echoforge.model.modelDownloader import (
    downloadModel,
)

from app.services.echoforge.model.modelUploader import (
    uploadModel,
)


def runOnboardingWorkflow(
    researchResult: dict,
) -> dict:

    # ----------------------------------------
    # 1. Resolve source + downloader
    # ----------------------------------------

    try:

        downloadDecision = resolveOnboardingDownload(researchResult)

    except Exception as error:

        modelName = researchResult.get("candidate", {}).get("name")

        return {
            "modelName": modelName,
            "status": "download-resolution-failed",
            "error": str(error),
        }

    modelName = downloadDecision["modelName"]

    print()
    print("=" * 60)
    print(f"[Onboarding Workflow] Starting: " f"{modelName}")
    print("=" * 60)

    print("[Onboarding Workflow] Source type: " f"{downloadDecision['sourceType']}")

    print("[Onboarding Workflow] Source: " f"{downloadDecision['source']}")

    # ----------------------------------------
    # 2. No usable downloader
    # ----------------------------------------

    if not downloadDecision["hasUsableDownloader"]:

        print("[Onboarding Workflow] " "No suitable downloader found.")

        return {
            **downloadDecision,
            "status": "downloader-required",
        }

    downloaderName = downloadDecision["downloader"]

    print("[Onboarding Workflow] Downloader: " f"{downloaderName}")

    # ----------------------------------------
    # 3. Ensure model_list entry exists
    # ----------------------------------------

    modelListEntryAdded = False

    try:

        existingModelListEntryBeforeDownload = downloadDecision.get(
            "existingModelListEntryBeforeDownload",
            False,
        )

        if existingModelListEntryBeforeDownload:

            print("[Onboarding Workflow] " "Model already exists in " "model_list.")

        else:

            modelListResult = addModelListEntry(
                downloaderName=downloaderName,
                source=downloadDecision["source"],
            )

            downloadDecision["modelListName"] = modelListResult["modelListName"]

            modelListEntryAdded = modelListResult["added"]

            if modelListEntryAdded:

                print(
                    "[Onboarding Workflow] "
                    f"Added model to "
                    f"{downloaderName}/model_list"
                )

            else:

                print("[Onboarding Workflow] " "Model already exists in " "model_list.")

    except Exception as error:

        print("[Onboarding Workflow] " "Could not prepare model_list: " f"{error}")

        return {
            **downloadDecision,
            "status": "download-resolution-failed",
            "error": str(error),
        }

    # ----------------------------------------
    # 4. Download model
    # ----------------------------------------

    downloadResult = None
    downloadError = None

    for attempt in range(2):

        try:

            print("[Onboarding Workflow] " f"Download attempt " f"{attempt + 1}/2")

            downloadResult = downloadModel(
                downloader={
                    "downloader": (downloadDecision["downloader"]),
                    "scope": (downloadDecision["scope"]),
                    "sourceType": (downloadDecision["sourceType"]),
                    "modelListName": (downloadDecision.get("modelListName")),
                    "cacheName": (downloadDecision.get("cacheName")),
                },
                modelName=modelName,
                sourceType=(downloadDecision["sourceType"]),
                source=(downloadDecision["source"]),
                cacheName=(downloadDecision.get("cacheName")),
            )

            downloadError = None

            break

        except Exception as error:

            downloadError = error

            print(
                "[Onboarding Workflow] "
                f"Download attempt "
                f"{attempt + 1}/2 failed: "
                f"{error}"
            )

    # ----------------------------------------
    # 5. Download failed after retry
    # ----------------------------------------

    if downloadError is not None:

        print("[Onboarding Workflow] " "Downloader failed after retry.")

        if modelListEntryAdded:

            try:

                removed = removeModelListEntry(
                    downloaderName=downloaderName,
                    source=downloadDecision["source"],
                )

                if removed:

                    print(
                        "[Onboarding Workflow] "
                        "Removed temporary "
                        "model_list entry."
                    )

            except Exception as error:

                print(
                    "[Onboarding Workflow] "
                    "Could not remove temporary "
                    f"model_list entry: {error}"
                )

        return {
            **downloadDecision,
            "status": "downloader-required",
            "error": str(downloadError),
        }

    # ----------------------------------------
    # 6. Persist updated model metadata
    # ----------------------------------------

    if modelListEntryAdded:

        try:

            modelInfo = buildModelInfo()

            writeModelInfo(modelInfo)

            print("[Onboarding Workflow] " "Updated model_info.json.")

        except Exception as error:

            print(
                "[Onboarding Workflow] " "Could not update " f"model_info.json: {error}"
            )

    # ----------------------------------------
    # 7. Upload/register model
    # ----------------------------------------

    try:

        uploadResult = uploadModel(
            cacheName=(downloadResult["cacheName"]),
            modelName=modelName,
        )

    except Exception as error:

        print("[Onboarding Workflow] " f"Upload failed: {error}")

        return {
            **downloadDecision,
            "status": "upload-failed",
            "modelListName": (downloadResult.get("modelListName")),
            "cacheName": (downloadResult.get("cacheName")),
            "cachePath": (downloadResult.get("cachePath")),
            "error": str(error),
        }

    clearmlModelId = uploadResult["clearmlModelId"]

    print("[Onboarding Workflow] " f"ClearML model ID: " f"{clearmlModelId}")

    # ----------------------------------------
    # 8. Completed
    # ----------------------------------------

    result = {
        **downloadDecision,
        "status": "completed",
        "modelListName": (downloadResult.get("modelListName")),
        "cacheName": (downloadResult["cacheName"]),
        "cachePath": (downloadResult["cachePath"]),
        "clearmlModelId": (clearmlModelId),
    }

    print("[Onboarding Workflow] " f"Completed: {modelName}")

    return result
