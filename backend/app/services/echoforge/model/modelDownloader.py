import subprocess
import sys

from app.services.echoforge.echoforgeConfig import (
    CACHE_DIR,
    MODEL_DOWNLOAD_DIR,
    getEchoforgeEnvironment,
)

MODEL_DOWNLOAD_SCRIPT = "models_download.py"


def downloadModel(
    downloader: dict,
    modelName: str,
    sourceType: str,
    source: str,
    cacheName: str | None = None,
) -> dict:

    downloaderName = downloader["downloader"]

    modelListName = downloader.get("modelListName")

    # ----------------------------------------
    # model_list entry is required
    # ----------------------------------------

    if not modelListName:

        raise RuntimeError(
            "No modelListName provided for " f"downloader: {downloaderName}"
        )

    # ----------------------------------------
    # Resolve actual cache directory
    # ----------------------------------------

    resolvedCacheName = downloader.get("cacheName") or cacheName or modelListName

    scriptPath = MODEL_DOWNLOAD_DIR / MODEL_DOWNLOAD_SCRIPT

    if not scriptPath.exists():

        raise RuntimeError("echoforge models_download.py " f"not found: {scriptPath}")

    # ----------------------------------------
    # Build echoforge command
    # ----------------------------------------

    command = [
        sys.executable,
        str(scriptPath),
        "--name",
        (f"{downloaderName}:" f"{modelListName}"),
    ]

    # ----------------------------------------
    # Logging
    # ----------------------------------------

    print()
    print("[Onboarding] Starting " "echoforge download")

    print(f"[Onboarding] Model: " f"{modelName}")

    print(f"[Onboarding] Source: " f"{source}")

    print(f"[Onboarding] Downloader: " f"{downloaderName}")

    print(f"[Onboarding] Model list name: " f"{modelListName}")

    print(f"[Onboarding] Cache name: " f"{resolvedCacheName}")

    print("[Onboarding] Command: " + " ".join(command))

    # ----------------------------------------
    # Run echoforge
    # ----------------------------------------

    env = getEchoforgeEnvironment()

    process = subprocess.Popen(
        command,
        cwd=str(MODEL_DOWNLOAD_DIR),
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

            print(f"[echoforge] {line}")

    returnCode = process.wait()

    # ----------------------------------------
    # Handle process failure
    # ----------------------------------------

    if returnCode != 0:

        raise RuntimeError(
            "echoforge model download failed." "\n\n" + "\n".join(outputLines)
        )

    # ----------------------------------------
    # Verify actual cache directory
    # ----------------------------------------

    cachePath = CACHE_DIR / resolvedCacheName

    if not cachePath.exists():

        raise RuntimeError(
            "echoforge download completed, "
            "but expected cache was not found: "
            f"{cachePath}"
        )

    # ----------------------------------------
    # Completed
    # ----------------------------------------

    return {
        "modelName": modelName,
        "sourceType": sourceType,
        "source": source,
        "downloader": downloaderName,
        "modelListName": modelListName,
        "cacheName": resolvedCacheName,
        "cachePath": str(cachePath),
        "status": "completed",
    }
