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

    # ----------------------------------------
    # 1. Resolve source + downloader
    # ----------------------------------------

    downloadDecision = resolveOnboardingDownload(researchResult)

    if not downloadDecision["hasUsableDownloader"]:

        return {
            **downloadDecision,
            "status": ("downloader-required"),
        }

    # ----------------------------------------
    # 2. Download
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
            modelName=(downloadDecision["modelName"]),
            sourceType=(downloadDecision["sourceType"]),
            source=(downloadDecision["source"]),
            cacheName=(downloadDecision.get("cacheName")),
        )

    except Exception as error:

        return {
            **downloadDecision,
            "status": ("download-failed"),
            "error": str(error),
        }

    # ----------------------------------------
    # 3. Upload/register
    # ----------------------------------------

    try:

        uploadResult = uploadModel(
            cacheName=(downloadResult["cacheName"]),
            modelName=(downloadDecision["modelName"]),
        )

    except Exception as error:

        return {
            **downloadDecision,
            "status": "upload-failed",
            "cacheName": (downloadResult.get("cacheName")),
            "cachePath": (downloadResult.get("cachePath")),
            "error": str(error),
        }

    # ----------------------------------------
    # 4. Completed
    # ----------------------------------------

    return {
        **downloadDecision,
        "status": "completed",
        "modelListName": (downloadResult.get("modelListName")),
        "cacheName": (downloadResult["cacheName"]),
        "cachePath": (downloadResult["cachePath"]),
        "clearmlModelId": (uploadResult["clearmlModelId"]),
    }
