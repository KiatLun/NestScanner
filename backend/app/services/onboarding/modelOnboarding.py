import time

from app.services.echoforge.echoforgeClient import (
    createDownloader,
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

    # 1. Ask EchoForge what downloaders it currently supports.
    capabilities = getDownloaderCapabilities()
    # 2. Try to resolve an existing downloader.
    downloader = resolveDownloader(
        modelName=modelName,
        sourceType=sourceType,
        capabilities=capabilities,
    )
    # 3. If no downloader exists, ask EchoForge to create one.
    if not downloader:
        downloaderName = modelName.lower().replace("/", "-").replace(" ", "-")

        createDownloader(
            name=downloaderName,
            modelName=modelName,
            sourceType=sourceType,
            source=source,
        )

        # Refresh EchoForge capabilities.
        capabilities = getDownloaderCapabilities()

        # Resolve again using the newly created capability.
        downloader = resolveDownloader(
            modelName=modelName,
            sourceType=sourceType,
            capabilities=capabilities,
        )

        if not downloader:
            raise RuntimeError("Downloader was created but " "could not be resolved.")

    downloaderName = downloader["name"]

    # 4. Use downloader-specific cache name if EchoForge defines one.
    resolvedCacheName = downloader.get("cacheName") or cacheName

    # 5. Start model download.
    downloadJob = startModelDownload(
        downloader=downloaderName,
        modelName=modelName,
        cacheName=resolvedCacheName,
        sourceType=sourceType,
        source=source,
    )

    # 6. Wait for download to complete.
    downloadResult = waitForJob(
        getStatus=getModelDownloadStatus,
        jobId=downloadJob["jobId"],
    )

    # 7. Start model upload.
    uploadJob = startModelUpload(
        cacheName=resolvedCacheName,
        modelName=modelName,
    )

    # 8. Wait for upload to complete.
    uploadResult = waitForJob(
        getStatus=getModelUploadStatus,
        jobId=uploadJob["jobId"],
    )

    return {
        "modelName": modelName,
        "sourceType": sourceType,
        "source": source,
        "downloader": downloaderName,
        "cacheName": resolvedCacheName,
        "cachePath": downloadResult["cachePath"],
        "clearmlModelId": uploadResult["clearmlModelId"],
        "status": "completed",
    }
