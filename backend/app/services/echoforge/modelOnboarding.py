from app.services.echoforge.modelInfoReader import (
    getAllModelInfo,
)

from app.services.echoforge.downloaderResolver import (
    resolveDownloader,
)

from app.services.echoforge.modelDownloader import (
    downloadModel,
)

from app.services.echoforge.modelUploader import (
    uploadModel,
)


def onboardModel(
    modelName: str,
    sourceType: str,
    source: str,
    cacheName: str | None = None,
) -> dict:

    print()
    print("=" * 60)
    print(f"[Onboarding] Starting: {modelName}")
    print("=" * 60)

    # ----------------------------------------
    # 1. Read EchoForge model information
    # ----------------------------------------

    modelInfo = getAllModelInfo()

    print(f"[Onboarding] Found " f"{len(modelInfo)} EchoForge downloaders")

    # ----------------------------------------
    # 2. Resolve downloader
    # ----------------------------------------

    downloader = resolveDownloader(
        modelName=modelName,
        sourceType=sourceType,
        source=source,
        modelInfo=modelInfo,
    )

    if not downloader:
        raise RuntimeError(
            "No suitable EchoForge downloader "
            f"found for '{modelName}'. "
            "Automatic downloader creation "
            "is currently TODO."
        )

    downloaderName = downloader["downloader"]

    print(f"[Onboarding] Resolved downloader: " f"{downloaderName}")

    if downloader.get("cacheName"):
        print(f"[Onboarding] Resolved cache: " f"{downloader['cacheName']}")

    # ----------------------------------------
    # 3. Download
    # ----------------------------------------

    downloadResult = downloadModel(
        downloader=downloader,
        modelName=modelName,
        sourceType=sourceType,
        source=source,
        cacheName=cacheName,
    )

    print(f"[Onboarding] Download completed: " f"{downloadResult['cachePath']}")

    # ----------------------------------------
    # 4. Upload to ClearML / MinIO
    # ----------------------------------------

    uploadResult = uploadModel(
        cacheName=downloadResult["cacheName"],
        modelName=modelName,
    )

    print(f"[Onboarding] Upload completed")

    print(f"[Onboarding] ClearML model ID: " f"{uploadResult['clearmlModelId']}")

    # ----------------------------------------
    # 5. Final result
    # ----------------------------------------

    result = {
        "modelName": modelName,
        "sourceType": sourceType,
        "source": source,
        "downloader": downloaderName,
        "cacheName": downloadResult["cacheName"],
        "cachePath": downloadResult["cachePath"],
        "clearmlModelId": uploadResult["clearmlModelId"],
        "status": "completed",
    }

    print(f"[Onboarding] Completed: {modelName}")

    return result
