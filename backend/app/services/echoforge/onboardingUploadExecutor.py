from app.services.echoforge.modelUploader import (
    uploadModel,
)


def executeOnboardingUpload(
    downloadResult: dict,
) -> dict:

    modelName = downloadResult["modelName"]

    cacheName = downloadResult["cacheName"]

    if downloadResult.get("status") != "downloaded":

        return {
            **downloadResult,
            "status": "upload-skipped",
        }

    uploadResult = uploadModel(
        cacheName=cacheName,
        modelName=modelName,
    )

    return {
        **downloadResult,
        "status": "completed",
        "clearmlModelId": uploadResult.get("clearmlModelId"),
    }
