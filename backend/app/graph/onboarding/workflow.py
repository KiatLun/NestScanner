from app.graph.onboarding.onboardingDownloadResolver import (
    resolveOnboardingDownload,
)

from app.services.echoforge.modelListManager import (
    addModelToModelList,
)

from app.services.echoforge.modelDownloader import (
    downloadModel,
)

from app.services.echoforge.modelUploader import (
    uploadModel,
)


def runOnboardingWorkflow(
    researchResult: dict,
) -> dict:

    # ----------------------------------------
    # 1. Resolve source + existing downloader
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

    print(f"[Onboarding Workflow] Source type: " f"{downloadDecision['sourceType']}")

    print(f"[Onboarding Workflow] Source: " f"{downloadDecision['source']}")

    # ----------------------------------------
    # 2. No usable existing downloader
    # ----------------------------------------

    if not downloadDecision["hasUsableDownloader"]:

        print("[Onboarding Workflow] " "No suitable downloader found.")

        return {
            **downloadDecision,
            "status": "downloader-required",
        }

    downloaderName = downloadDecision["downloader"]

    print(f"[Onboarding Workflow] Downloader: " f"{downloaderName}")

    # ----------------------------------------
    # 3. Download model
    # ----------------------------------------

    downloadResult = None
    downloadError = None

    for attempt in range(2):

        try:

            print(
                f"[Onboarding Workflow] "
                f"Download attempt {attempt + 1}/2"
            )

            downloadResult = downloadModel(
                downloader={
                    "downloader": downloadDecision["downloader"],
                    "scope": downloadDecision["scope"],
                    "sourceType": downloadDecision["sourceType"],
                    "modelListName": downloadDecision.get("modelListName"),
                    "cacheName": downloadDecision.get("cacheName"),
                },
                modelName=modelName,
                sourceType=downloadDecision["sourceType"],
                source=downloadDecision["source"],
                cacheName=downloadDecision.get("cacheName"),
            )

            downloadError = None
            break

        except Exception as error:

            downloadError = error

            print(
                f"[Onboarding Workflow] "
                f"Download attempt {attempt + 1}/2 failed: {error}"
            )

    if downloadError is not None:

        print(
            "[Onboarding Workflow] "
            "Downloader failed after retry."
        )

        return {
            **downloadDecision,
            "status": "downloader-required",
            "error": str(downloadError),
        }

    # ----------------------------------------
    # 4. Persist successful downloader mapping
    # ----------------------------------------

    try:

        modelListResult = addModelToModelList(
            downloaderName=downloadDecision["downloader"],
            source=downloadDecision["source"],
            modelListName=downloadResult["cacheName"],
        )

        if modelListResult["added"]:
            print(
                "[Onboarding Workflow] "
                f"Added model to {downloadDecision['downloader']}/model_list"
            )
        else:
            print(
                "[Onboarding Workflow] "
                "Model already exists in model_list."
            )

    except Exception as error:

        print(
            "[Onboarding Workflow] "
            f"Could not update model_list: {error}"
        )

    # ----------------------------------------
    # 5. Upload/register model
    # ----------------------------------------

    try:

        uploadResult = uploadModel(
            cacheName=downloadResult["cacheName"],
            modelName=modelName,
        )

    except Exception as error:

        print("[Onboarding Workflow] " f"Upload failed: {error}")

        return {
            **downloadDecision,
            "status": "upload-failed",
            "modelListName": downloadResult.get("modelListName"),
            "cacheName": downloadResult.get("cacheName"),
            "cachePath": downloadResult.get("cachePath"),
            "error": str(error),
        }

    # ----------------------------------------
    # 6. Completed
    # ----------------------------------------

    result = {
        **downloadDecision,
        "status": "completed",
        "modelListName": downloadResult.get("modelListName"),
        "cacheName": downloadResult["cacheName"],
        "cachePath": downloadResult["cachePath"],
        "clearmlModelId": uploadResult["clearmlModelId"],
    }

    print(f"[Onboarding Workflow] Completed: " f"{modelName}")

    return result
