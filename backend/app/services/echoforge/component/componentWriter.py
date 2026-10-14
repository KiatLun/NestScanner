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

    # ----------------------------------------
    # 1. Write generated component files
    # ----------------------------------------

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

    # ----------------------------------------
    # 2. Record generated files for GitHub PR
    # ----------------------------------------

    echoforgeRoot = COMPONENTS_DIR.parent

    generatedFiles = [
        filePath.relative_to(echoforgeRoot).as_posix()
        for filePath in (
            mainFile,
            requirementsFile,
            dockerfile,
        )
    ]

    print(
        "[Component Writer] " f"Recorded {len(generatedFiles)} files " "for GitHub PR."
    )

    # ----------------------------------------
    # 3. Return component information
    # ----------------------------------------

    return {
        "component": componentName,
        "componentDir": str(componentDir),
        "mainFile": str(mainFile),
        "requirementsFile": str(requirementsFile),
        "dockerfile": str(dockerfile),
        "buildContext": str(COMPONENTS_DIR),
        "generatedFiles": generatedFiles,
    }
