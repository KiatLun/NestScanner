import json

from app.services.echoforge.echoforgeConfig import (
    MODEL_INFO_FILE,
)


def getAllModelInfo() -> list[dict]:
    if not MODEL_INFO_FILE.exists():
        raise RuntimeError(
            f"EchoForge model info file not found: " f"{MODEL_INFO_FILE}"
        )

    with MODEL_INFO_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        modelInfo = json.load(file)

    if not isinstance(modelInfo, list):
        raise RuntimeError("model_info.json must contain a list.")

    return modelInfo


def getAllSupportedModels() -> list[dict]:
    modelInfo = getAllModelInfo()

    models = []

    for entry in modelInfo:
        downloader = entry.get("downloader")
        scope = entry.get("scope")
        sourceType = entry.get("sourceType")

        supportedModels = entry.get(
            "supportedModels",
            [],
        )

        for supportedModel in supportedModels:
            models.append(
                {
                    "source": supportedModel.get("source"),
                    "cacheName": supportedModel.get("cacheName"),
                    "downloader": downloader,
                    "scope": scope,
                    "sourceType": sourceType,
                }
            )

    return models
