from app.graph.onboarding.downloadSourceResolver import (
    resolveDownloadSource,
)

from app.services.echoforge.modelInfoReader import (
    getAllModelInfo,
)

from app.graph.onboarding.downloaderResolver import (
    resolveDownloader,
)


def resolveOnboardingDownload(
    researchResult: dict,
) -> dict:

    # ----------------------------------------
    # 1. Resolve actual model weight source
    # ----------------------------------------

    sourceResult = resolveDownloadSource(researchResult)

    modelName = sourceResult["modelName"]

    sourceType = sourceResult["sourceType"]

    source = sourceResult["source"]

    # ----------------------------------------
    # 2. Read echoforge downloader metadata
    # ----------------------------------------

    modelInfo = getAllModelInfo()

    # ----------------------------------------
    # 3. Find suitable downloader
    # ----------------------------------------

    downloaderResult = resolveDownloader(
        modelName=modelName,
        sourceType=sourceType,
        source=source,
        modelInfo=modelInfo,
    )

    # ----------------------------------------
    # 4. No suitable downloader
    # ----------------------------------------

    if not downloaderResult:

        return {
            "modelName": modelName,
            "sourceType": sourceType,
            "source": source,
            "sourceReason": (sourceResult.get("reason")),
            "hasUsableDownloader": False,
            "downloader": None,
            "scope": None,
            "modelListName": None,
            "cacheName": None,
            "existingModelListEntryBeforeDownload": False,
        }

    # ----------------------------------------
    # 5. Downloader found
    # ----------------------------------------

    return {
        "modelName": modelName,
        "sourceType": sourceType,
        "source": source,
        "sourceReason": (sourceResult.get("reason")),
        "hasUsableDownloader": True,
        "downloader": (downloaderResult.get("downloader")),
        "scope": (downloaderResult.get("scope")),
        "modelListName": (downloaderResult.get("modelListName")),
        "cacheName": (downloaderResult.get("cacheName")),
        "existingModelListEntryBeforeDownload": (
            downloaderResult.get(
                "existingModelListEntryBeforeDownload",
                False,
            )
        ),
    }
