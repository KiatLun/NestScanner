from pathlib import Path

from app.services.echoforge.echoforgeConfig import (
    COMPONENTS_DIR,
)

STT_INFERENCE_DIR = COMPONENTS_DIR / "inference_component" / "stt_inference"


def writeGeneratedComponent(
    componentName: str,
    mainFileContent: str,
    requirementsContent: str,
    dockerfileContent: str,
) -> dict:

    componentDir = STT_INFERENCE_DIR / componentName

    componentDir.mkdir(
        parents=True,
        exist_ok=True,
    )

    mainFile = componentDir / "main.py"

    requirementsFile = componentDir / "requirements.txt"

    dockerfile = componentDir / "Dockerfile"

    mainFile.write_text(
        mainFileContent,
        encoding="utf-8",
    )

    requirementsFile.write_text(
        requirementsContent,
        encoding="utf-8",
    )

    dockerfile.write_text(
        dockerfileContent,
        encoding="utf-8",
    )

    return {
        "component": componentName,
        "componentDir": str(componentDir),
        "mainFile": str(mainFile),
        "requirementsFile": str(requirementsFile),
        "dockerfile": str(dockerfile),
        "buildContext": str(COMPONENTS_DIR),
    }
