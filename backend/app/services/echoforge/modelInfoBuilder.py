import ast
import json
from pathlib import Path

from app.services.echoforge.echoforgeConfig import (
    MODEL_DOWNLOAD_DIR,
    MODEL_INFO_FILE,
)

GENERIC_DOWNLOADERS = {
    "hugging_face_download": {
        "sourceType": "huggingface",
        "scope": "generic",
    },
}


SOURCE_TYPES = {
    "brouhaha_download": "github",
    "omnilingual_download": "github",
    "pyannote_download": "huggingface",
    "silero_download": "github",
    "trvad_download": "github",
    "voxtral_download": "huggingface",
    "whisper_download": "huggingface",
}


def parseModelList(
    modelListPath: Path,
) -> list[tuple[str, str]]:

    models = []

    if not modelListPath.exists():
        return models

    for rawLine in modelListPath.read_text(encoding="utf-8").splitlines():

        line = rawLine.strip()

        if not line:
            continue

        if line.startswith("#"):
            continue

        parts = line.split()

        source = parts[0]

        modelListName = parts[1] if len(parts) >= 2 else source.split("/")[-1]

        models.append(
            (
                source,
                modelListName,
            )
        )

    return models


def getModelName(
    downloadFile: Path,
) -> str | None:

    if not downloadFile.exists():
        return None

    try:

        tree = ast.parse(downloadFile.read_text(encoding="utf-8"))

    except Exception:

        return None

    for node in ast.walk(tree):

        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            continue

        if node.name != "model_name":
            continue

        for child in ast.walk(node):

            if not isinstance(
                child,
                ast.Return,
            ):
                continue

            value = child.value

            if isinstance(
                value,
                ast.Constant,
            ) and isinstance(
                value.value,
                str,
            ):
                return value.value

    return None


def buildModelInfo() -> list[dict]:

    modelInfo = []

    if not MODEL_DOWNLOAD_DIR.exists():
        raise FileNotFoundError(
            f"Model download directory not found: " f"{MODEL_DOWNLOAD_DIR}"
        )

    for folder in sorted(MODEL_DOWNLOAD_DIR.iterdir()):

        if not folder.is_dir():
            continue

        downloadFile = folder / "download.py"

        if not downloadFile.exists():
            continue

        downloaderName = folder.name

        genericConfig = GENERIC_DOWNLOADERS.get(downloaderName)

        # ------------------------------------
        # Determine downloader type
        # ------------------------------------

        if genericConfig:

            scope = genericConfig["scope"]

            sourceType = genericConfig["sourceType"]

        else:

            scope = "model-specific"

            sourceType = SOURCE_TYPES.get(downloaderName)

        if not sourceType:
            continue

        # ------------------------------------
        # Read model_list
        # ------------------------------------

        modelListPath = folder / "model_list"

        listedModels = parseModelList(modelListPath)

        supportedModels = []

        # ------------------------------------
        # Generic downloader
        # ------------------------------------

        if scope == "generic":

            for (
                source,
                modelListName,
            ) in listedModels:

                supportedModels.append(
                    {
                        "source": (source),
                        "modelListName": (modelListName),
                        "cacheName": (modelListName),
                    }
                )

        # ------------------------------------
        # Model-specific downloader
        # ------------------------------------

        else:

            modelName = getModelName(downloadFile)

            if not modelName:

                modelName = downloaderName.removesuffix("_download")

            for (
                source,
                modelListName,
            ) in listedModels:

                supportedModels.append(
                    {
                        "source": (source),
                        "modelListName": (modelListName),
                        "cacheName": (modelName),
                    }
                )

            # --------------------------------
            # Model-specific downloader
            # without model_list
            # --------------------------------

            if not listedModels:

                supportedModels.append(
                    {
                        "source": (modelName),
                        "modelListName": None,
                        "cacheName": (modelName),
                    }
                )

        # ------------------------------------
        # Add downloader metadata
        # ------------------------------------

        modelInfo.append(
            {
                "downloader": (downloaderName),
                "scope": (scope),
                "sourceType": (sourceType),
                "supportedModels": (supportedModels),
            }
        )

    return modelInfo


def writeModelInfo(
    modelInfo: list[dict],
) -> None:

    MODEL_INFO_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    MODEL_INFO_FILE.write_text(
        json.dumps(
            modelInfo,
            indent=2,
        ),
        encoding="utf-8",
    )


def main():

    modelInfo = buildModelInfo()

    writeModelInfo(modelInfo)

    print(f"Generated model_info.json: " f"{MODEL_INFO_FILE}")

    print(f"Downloaders: {len(modelInfo)}")


if __name__ == "__main__":
    main()
