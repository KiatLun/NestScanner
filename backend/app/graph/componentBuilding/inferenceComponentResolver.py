from app.services.echoforge.echoforgeConfig import (
    STT_INFERENCE_DIR,
    NESTSCANNER_EVALUATION_IMAGE,
)

COMPONENT_PREFIX = "stt_inference_"


def normalizeName(
    value: str,
) -> str:

    return value.strip().lower().replace("-", "").replace("_", "").replace(" ", "")


def getComponentFamily(
    componentName: str,
) -> str | None:

    if not componentName.startswith(COMPONENT_PREFIX):
        return None

    familyName = componentName.removeprefix(COMPONENT_PREFIX)

    if not familyName:
        return None

    return familyName


def getAvailableInferenceComponents() -> list[dict]:

    if not STT_INFERENCE_DIR.exists():
        raise RuntimeError(
            "EchoForge STT inference directory " f"not found: {STT_INFERENCE_DIR}"
        )

    components = []

    for folder in sorted(STT_INFERENCE_DIR.iterdir()):

        if not folder.is_dir():
            continue

        componentName = folder.name

        familyName = getComponentFamily(componentName)

        if not familyName:
            continue

        mainFile = folder / "main.py"

        dockerfile = folder / "Dockerfile"

        requirementsFile = folder / "requirements.txt"

        # Component must contain an executable main.py
        if not mainFile.exists():
            continue

        entryPoint = (
            f"/app/inference_component/"
            f"stt_inference/"
            f"{componentName}/"
            f"main.py"
        )

        components.append(
            {
                "component": componentName,
                "family": familyName,
                "componentDir": str(folder),
                "mainFile": str(mainFile),
                "dockerfile": (str(dockerfile) if dockerfile.exists() else None),
                "requirementsFile": (
                    str(requirementsFile) if requirementsFile.exists() else None
                ),
                # Runtime information used by EchoForge pipeline
                "imageName": NESTSCANNER_EVALUATION_IMAGE,
                "entryPoint": entryPoint,
            }
        )

    return components


def resolveInferenceComponent(
    modelName: str,
    source: str,
) -> dict | None:

    normalizedModelName = normalizeName(modelName)

    sourceName = source.strip().split("/")[-1]

    normalizedSourceName = normalizeName(sourceName)

    components = getAvailableInferenceComponents()

    for component in components:

        familyName = component["family"]

        normalizedFamilyName = normalizeName(familyName)

        familyMatches = (
            normalizedFamilyName in normalizedModelName
            or normalizedFamilyName in normalizedSourceName
        )

        if not familyMatches:
            continue

        return {
            **component,
            "modelName": modelName,
            "source": source,
            "matchedBy": "model-family",
        }

    return None
