import time
import requests

ECHOFORGE_API_URL = "http://localhost:8100"


def getDownloaderCapabilities() -> list[dict]:
    response = requests.get(
        f"{ECHOFORGE_API_URL}/api/capabilities/downloaders",
        timeout=10,
    )

    response.raise_for_status()

    return response.json().get(
        "downloaders",
        [],
    )


def startModelDownload(
    downloader: str,
    modelName: str,
    cacheName: str,
    sourceType: str,
    source: str,
) -> dict:

    response = requests.post(
        f"{ECHOFORGE_API_URL}/api/models/download",
        json={
            "downloader": downloader,
            "modelName": modelName,
            "cacheName": cacheName,
            "sourceType": sourceType,
            "source": source,
        },
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def getModelDownloadStatus(
    jobId: str,
) -> dict:

    response = requests.get(
        f"{ECHOFORGE_API_URL}/api/models/download/{jobId}",
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def startModelUpload(
    cacheName: str,
    modelName: str,
    project: str = "model-registry",
) -> dict:

    response = requests.post(
        f"{ECHOFORGE_API_URL}/api/models/upload",
        json={
            "cacheName": cacheName,
            "modelName": modelName,
            "project": project,
        },
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def getModelUploadStatus(
    jobId: str,
) -> dict:

    response = requests.get(
        f"{ECHOFORGE_API_URL}/api/models/upload/{jobId}",
        timeout=10,
    )

    response.raise_for_status()

    return response.json()
