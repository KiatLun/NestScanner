from app.services.echoforge.onboardingDownloadResolver import (
    resolveOnboardingDownload,
)

from app.services.echoforge.modelDownloader import (
    downloadModel,
)

from app.services.echoforge.modelUploader import (
    uploadModel,
)


def executeOnboardingDownloadAndUpload(
    researchResult: dict,
) -> dict:

    # 1. Resolve source + downloader
    downloadDecision = resolveOnboardingDownload(researchResult)

    if not downloadDecision["hasUsableDownloader"]:
        return {
            **downloadDecision,
            "status": "needs-downloader",
        }

    # 2. Download model
    try:
        downloadResult = downloadModel(
            downloader={
                "downloader": downloadDecision["downloader"],
                "scope": downloadDecision["scope"],
                "sourceType": downloadDecision["sourceType"],
                "cacheName": downloadDecision["cacheName"],
            },
            modelName=downloadDecision["modelName"],
            sourceType=downloadDecision["sourceType"],
            source=downloadDecision["source"],
            cacheName=downloadDecision["cacheName"],
        )

    except Exception as error:
        return {
            **downloadDecision,
            "status": "download-failed",
            "error": str(error),
        }

    # 3. Upload/register model
    try:
        uploadResult = uploadModel(
            cacheName=downloadResult["cacheName"],
            modelName=downloadDecision["modelName"],
        )

    except Exception as error:
        return {
            **downloadDecision,
            "status": "upload-failed",
            "cacheName": downloadResult.get("cacheName"),
            "cachePath": downloadResult.get("cachePath"),
            "error": str(error),
        }

    # 4. Completed
    return {
        **downloadDecision,
        "status": "completed",
        "cacheName": downloadResult["cacheName"],
        "cachePath": downloadResult["cachePath"],
        "clearmlModelId": uploadResult["clearmlModelId"],
    }
