import subprocess
import sys

from app.services.echoforge.echoforgeConfig import (
    IMAGE_BUILDER_FILE,
    IMAGE_DOWNLOADER_DIR,
    getEchoforgeEnvironment,
)


def buildComponentImage(
    componentName: str,
) -> dict:

    if not IMAGE_BUILDER_FILE.exists():
        raise RuntimeError(
            "EchoForge image builder not found: " f"{IMAGE_BUILDER_FILE}"
        )

    command = [
        sys.executable,
        str(IMAGE_BUILDER_FILE),
        "--name",
        componentName,
    ]

    print()
    print("[Component] Building EchoForge image")

    print(f"[Component] Component: " f"{componentName}")

    print("[Component] Command: " + " ".join(command))

    env = getEchoforgeEnvironment()

    process = subprocess.Popen(
        command,
        cwd=str(IMAGE_DOWNLOADER_DIR),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    outputLines = []

    if process.stdout:

        for line in process.stdout:

            line = line.rstrip()

            outputLines.append(line)

            print(f"[EchoForge] {line}")

    returnCode = process.wait()

    if returnCode != 0:

        raise RuntimeError(
            "EchoForge component image build failed." "\n\n" + "\n".join(outputLines)
        )

    return {
        "component": componentName,
        "status": "completed",
    }
