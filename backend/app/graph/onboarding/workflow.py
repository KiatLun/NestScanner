from app.graph.onboarding.onboardingDownloadResolver import (
    resolveOnboardingDownload,
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

    try:

        downloadResult = downloadModel(
            downloader={
                "downloader": (downloadDecision["downloader"]),
                "scope": (downloadDecision["scope"]),
                "sourceType": (downloadDecision["sourceType"]),
                "modelListName": (downloadDecision.get("modelListName")),
                "cacheName": (downloadDecision.get("cacheName")),
            },
            modelName=modelName,
            sourceType=downloadDecision["sourceType"],
            source=downloadDecision["source"],
            cacheName=downloadDecision.get("cacheName"),
        )

    except Exception as error:

        print("[Onboarding Workflow] " f"Download failed: {error}")

        return {
            **downloadDecision,
            "status": "download-failed",
            "error": str(error),
        }

    # ----------------------------------------
    # 4. Upload/register model
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
    # 5. Completed
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
