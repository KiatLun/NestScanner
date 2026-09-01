import time

from app.services.echoforge.echoforgeClient import (
    getDownloaderCapabilities,
    startModelDownload,
    getModelDownloadStatus,
    startModelUpload,
    getModelUploadStatus,
)

from app.services.echoforge.downloadResolver import (
    resolveDownloader,
)


def waitForJob(
    getStatus,
    jobId: str,
    pollSeconds: int = 2,
) -> dict:

    while True:
        result = getStatus(jobId)

        status = result.get("status")

        if status == "completed":
            return result

        if status == "failed":
            raise RuntimeError(
                result.get(
                    "error",
                    "EchoForge job failed.",
                )
            )

        time.sleep(pollSeconds)


def onboardModel(
    modelName: str,
    sourceType: str,
    source: str,
    cacheName: str | None = None,
) -> dict:

    cacheName = cacheName or modelName

    # 1. Ask EchoForge what it supports.
    capabilities = getDownloaderCapabilities()

    # 2. Resolve the appropriate downloader.
    downloader = resolveDownloader(
        modelName=modelName,
        sourceType=sourceType,
        capabilities=capabilities,
    )

    if not downloader:
        return {
            "modelName": modelName,
            "status": "unsupported",
            "reason": ("No compatible EchoForge " "downloader found."),
        }

    downloaderName = downloader["name"]

    # 3. Start download.
    downloadJob = startModelDownload(
        downloader=downloaderName,
        modelName=modelName,
        cacheName=cacheName,
        sourceType=sourceType,
        source=source,
    )

    # 4. Wait for download.
    downloadResult = waitForJob(
        getStatus=getModelDownloadStatus,
        jobId=downloadJob["jobId"],
    )

    # 5. Start upload.
    uploadJob = startModelUpload(
        cacheName=cacheName,
        modelName=modelName,
    )

    # 6. Wait for upload.
    uploadResult = waitForJob(
        getStatus=getModelUploadStatus,
        jobId=uploadJob["jobId"],
    )

    return {
        "modelName": modelName,
        "sourceType": sourceType,
        "source": source,
        "downloader": downloaderName,
        "cacheName": cacheName,
        "cachePath": downloadResult["cachePath"],
        "clearmlModelId": uploadResult["clearmlModelId"],
        "status": "completed",
    }
