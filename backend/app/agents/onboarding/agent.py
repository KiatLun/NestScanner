from app.services.echoforge.modelInfoReader import (
    getAllModelInfo,
)

from app.services.echoforge.downloadSourceResolver import (
    determineDownloadSource,
)

from app.services.echoforge.downloadResolver import (
    resolveDownloader,
)

from app.services.echoforge.modelDownloader import (
    downloadModel,
)

from app.services.echoforge.modelUploader import (
    uploadModel,
)


def onboardingAgent(
    onboardingInput: dict,
) -> dict:

    modelName = onboardingInput["modelName"]

    researchEvidence = onboardingInput.get(
        "researchEvidence",
        {},
    )

    technicalProfile = onboardingInput.get(
        "technicalProfile",
        {},
    )

    print()
    print("=" * 60)
    print(f"[Onboarding Agent] Starting: " f"{modelName}")
    print("=" * 60)

    # ----------------------------------------
    # 1. Determine actual download source
    # ----------------------------------------

    try:

        onboardingInput = determineDownloadSource(onboardingInput)

    except Exception as error:

        return {
            "modelName": modelName,
            "status": "source-resolution-failed",
            "researchEvidence": researchEvidence,
            "technicalProfile": technicalProfile,
            "error": str(error),
        }

    sourceType = onboardingInput["sourceType"]

    source = onboardingInput["source"]

    sourceReason = onboardingInput.get("sourceReason")

    print(f"[Onboarding Agent] Source type: " f"{sourceType}")

    print(f"[Onboarding Agent] Source: " f"{source}")

    # ----------------------------------------
    # 2. Read echoforge model information
    # ----------------------------------------

    modelInfo = getAllModelInfo()

    # ----------------------------------------
    # 3. Resolve existing downloader
    # ----------------------------------------

    downloader = resolveDownloader(
        modelName=modelName,
        sourceType=sourceType,
        source=source,
        modelInfo=modelInfo,
    )

    if not downloader:

        print("[Onboarding Agent] " "No suitable downloader found.")

        return {
            "modelName": modelName,
            "status": "needs-downloader",
            "sourceType": sourceType,
            "source": source,
            "sourceReason": sourceReason,
            "researchEvidence": researchEvidence,
            "technicalProfile": technicalProfile,
        }

    downloaderName = downloader["downloader"]

    print(f"[Onboarding Agent] Downloader: " f"{downloaderName}")

    # ----------------------------------------
    # 4. Attempt download
    # ----------------------------------------

    try:

        downloadResult = downloadModel(
            downloader=downloader,
            modelName=modelName,
            sourceType=sourceType,
            source=source,
            cacheName=downloader.get("cacheName"),
        )

    except Exception as error:

        print("[Onboarding Agent] " f"Download failed: {error}")

        return {
            "modelName": modelName,
            "status": "download-failed",
            "sourceType": sourceType,
            "source": source,
            "sourceReason": sourceReason,
            "downloader": downloaderName,
            "researchEvidence": researchEvidence,
            "technicalProfile": technicalProfile,
            "error": str(error),
        }

    # ----------------------------------------
    # 5. Upload/register model
    # ----------------------------------------

    try:

        uploadResult = uploadModel(
            cacheName=downloadResult["cacheName"],
            modelName=modelName,
        )

    except Exception as error:

        print("[Onboarding Agent] " f"Upload failed: {error}")

        return {
            "modelName": modelName,
            "status": "upload-failed",
            "sourceType": sourceType,
            "source": source,
            "sourceReason": sourceReason,
            "downloader": downloaderName,
            "cacheName": downloadResult.get("cacheName"),
            "cachePath": downloadResult.get("cachePath"),
            "error": str(error),
        }

    # ----------------------------------------
    # 6. Completed
    # ----------------------------------------

    result = {
        "modelName": modelName,
        "status": "completed",
        "sourceType": sourceType,
        "source": source,
        "sourceReason": sourceReason,
        "downloader": downloaderName,
        "cacheName": downloadResult["cacheName"],
        "cachePath": downloadResult["cachePath"],
        "clearmlModelId": uploadResult["clearmlModelId"],
    }

    print(f"[Onboarding Agent] Completed: " f"{modelName}")

    return result
