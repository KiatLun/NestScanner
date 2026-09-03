import json

from app.services.echoforge.echoforgeConfig import (
    MODEL_INFO_FILE,
)


def getAllModelInfo() -> list[dict]:

    if not MODEL_INFO_FILE.exists():
        raise RuntimeError(
            f"EchoForge model info file not found: " f"{MODEL_INFO_FILE}"
        )

    try:
        with MODEL_INFO_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            modelInfo = json.load(file)

    except Exception as error:
        raise RuntimeError("Failed to read EchoForge " f"model_info.json: {error}")

    if not isinstance(modelInfo, list):
        raise RuntimeError("EchoForge model_info.json " "must contain a list.")

    return modelInfo
