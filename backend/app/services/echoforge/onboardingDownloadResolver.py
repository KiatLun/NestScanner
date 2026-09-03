from app.services.echoforge.downloadSourceResolver import (
    resolveDownloadSource,
)

from app.services.echoforge.modelInfoReader import (
    getAllModelInfo,
)

from app.services.echoforge.downloadResolver import (
    resolveDownloader,
)


def resolveOnboardingDownload(
    researchResult: dict,
) -> dict:

    sourceResult = resolveDownloadSource(researchResult)

    modelName = sourceResult["modelName"]

    sourceType = sourceResult["sourceType"]

    source = sourceResult["source"]

    modelInfo = getAllModelInfo()

    downloaderResult = resolveDownloader(
        modelName=modelName,
        sourceType=sourceType,
        source=source,
        modelInfo=modelInfo,
    )

    if not downloaderResult:

        return {
            "modelName": modelName,
            "sourceType": sourceType,
            "source": source,
            "sourceReason": sourceResult.get("reason"),
            "hasUsableDownloader": False,
            "downloader": None,
            "scope": None,
            "cacheName": None,
        }

    return {
        "modelName": modelName,
        "sourceType": sourceType,
        "source": source,
        "sourceReason": sourceResult.get("reason"),
        "hasUsableDownloader": True,
        "downloader": downloaderResult.get("downloader"),
        "scope": downloaderResult.get("scope"),
        "cacheName": downloaderResult.get("cacheName"),
    }
