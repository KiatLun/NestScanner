import subprocess
from pathlib import Path

ECHOFORGE_PATH = Path("/mnt/c/Users/AJ/Desktop/echoforge")


def uploadModel(
    cacheName: str,
    modelName: str,
    project: str = "model-registry",
) -> dict:

    modelsUploadPath = ECHOFORGE_PATH / "deployment" / "models_upload"

    scriptPath = modelsUploadPath / "models_upload.py"

    envFilePath = ECHOFORGE_PATH / "services" / "clearml-agent" / "clearml.env"

    cachePath = ECHOFORGE_PATH / "deployment" / ".cache" / cacheName

    if not scriptPath.exists():
        raise FileNotFoundError(f"EchoForge uploader not found: " f"{scriptPath}")

    if not envFilePath.exists():
        raise FileNotFoundError(f"ClearML env file not found: " f"{envFilePath}")

    if not cachePath.exists():
        raise FileNotFoundError(f"Model cache not found: " f"{cachePath}")

    command = [
        "python3",
        "models_upload.py",
        "--name",
        cacheName,
        "--model-name",
        modelName,
        "--project",
        project,
        "--env-file",
        str(envFilePath),
    ]

    print("\n=== ECHOFORGE MODEL UPLOAD ===")

    print(f"Cache name: {cacheName}")

    print(f"Model name: {modelName}")

    print(f"Project: {project}")

    result = subprocess.run(
        command,
        cwd=modelsUploadPath,
        capture_output=True,
        text=True,
    )

    if result.stdout:
        print(
            result.stdout,
            end="",
        )

    if result.stderr:
        print(
            result.stderr,
            end="",
        )

    if result.returncode != 0:
        raise RuntimeError("EchoForge model upload failed.")

    clearmlModelId = None

    for line in result.stdout.splitlines():

        strippedLine = line.strip()

        if strippedLine.startswith("CLEARML_MODEL_ID="):
            clearmlModelId = strippedLine.split(
                "=",
                1,
            )[1].strip()

            break

    if not clearmlModelId:
        raise RuntimeError(
            "EchoForge upload completed but " "no ClearML model ID was returned."
        )

    return {
        "cacheName": cacheName,
        "modelName": modelName,
        "project": project,
        "clearmlModelId": clearmlModelId,
        "status": "completed",
    }
