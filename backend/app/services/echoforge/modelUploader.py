import re
import subprocess
import sys

from app.services.echoforge.echoforgeConfig import (
    MODEL_UPLOAD_DIR,
    CLEARML_ENV_FILE,
)

CLEARML_MODEL_ID_PATTERN = re.compile(r"CLEARML_MODEL_ID=([A-Za-z0-9_-]+)")


def uploadModel(
    cacheName: str,
    modelName: str,
    project: str = "model-registry",
) -> dict:

    scriptPath = MODEL_UPLOAD_DIR / "models_upload.py"

    if not scriptPath.exists():
        raise RuntimeError(f"EchoForge upload script not found: " f"{scriptPath}")

    if not CLEARML_ENV_FILE.exists():
        raise RuntimeError(f"ClearML env file not found: " f"{CLEARML_ENV_FILE}")

    command = [
        sys.executable,
        str(scriptPath),
        "--name",
        cacheName,
        "--model-name",
        modelName,
        "--project",
        project,
        "--env-file",
        str(CLEARML_ENV_FILE),
    ]

    print()
    print("[Onboarding] Starting EchoForge upload")
    print(f"[Onboarding] Model: {modelName}")
    print(f"[Onboarding] Cache name: {cacheName}")

    process = subprocess.Popen(
        command,
        cwd=str(MODEL_UPLOAD_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    outputLines = []
    clearmlModelId = None

    if process.stdout:

        for line in process.stdout:

            line = line.rstrip()

            outputLines.append(line)

            print(f"[EchoForge] {line}")

            match = CLEARML_MODEL_ID_PATTERN.search(line)

            if match:
                clearmlModelId = match.group(1)

    returnCode = process.wait()

    if returnCode != 0:
        raise RuntimeError(
            "EchoForge model upload failed." "\n\n" + "\n".join(outputLines)
        )

    if not clearmlModelId:
        raise RuntimeError(
            "EchoForge upload completed, "
            "but no CLEARML_MODEL_ID "
            "was found in the output."
        )

    return {
        "modelName": modelName,
        "cacheName": cacheName,
        "project": project,
        "clearmlModelId": clearmlModelId,
        "status": "completed",
    }


from app.services.echoforge.modelUploader import (
    uploadModel,
)


def main():

    result = uploadModel(
        cacheName="silero",
        modelName="silero",
    )

    print()
    print("UPLOAD RESULT:")
    print(result)


if __name__ == "__main__":
    main()
