from app.services.echoforge.modelDownloader import (
    downloadHuggingFaceModel,
)
from app.services.echoforge.modelUploader import (
    uploadModel,
)


def prepareModel(
    repoId: str,
    cacheName: str,
    modelName: str,
) -> dict:

    print("\n=== PREPARE MODEL ===")

    downloadResult = downloadHuggingFaceModel(
        repoId=repoId,
        cacheName=cacheName,
    )

    uploadResult = uploadModel(
        cacheName=cacheName,
        modelName=modelName,
    )

    clearmlModelId = uploadResult["clearmlModelId"]

    return {
        "repoId": repoId,
        "cacheName": cacheName,
        "modelName": modelName,
        "clearmlModelId": clearmlModelId,
        "download": downloadResult,
        "upload": uploadResult,
        "status": "completed",
    }
