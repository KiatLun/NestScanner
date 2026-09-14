import subprocess
import sys

from app.services.echoforge.echoforgeConfig import (
    CACHE_DIR,
    MODEL_DOWNLOAD_DIR,
    getEchoforgeEnvironment,
)

GENERIC_HF_DOWNLOADER = "hugging_face_download"
MODEL_DOWNLOAD_SCRIPT = "models_download.py"


def downloadModel(
    downloader: dict,
    modelName: str,
    sourceType: str,
    source: str,
    cacheName: str | None = None,
) -> dict:

    downloaderName = downloader["downloader"]

    scope = downloader.get("scope")

    modelListName = downloader.get("modelListName")

    # ----------------------------------------
    # Resolve actual cache directory
    # ----------------------------------------

    resolvedCacheName = (
        downloader.get("cacheName")
        or cacheName
        or modelName.replace(
            "/",
            "-",
        ).replace(
            " ",
            "-",
        )
    )

    scriptPath = MODEL_DOWNLOAD_DIR / MODEL_DOWNLOAD_SCRIPT

    if not scriptPath.exists():

        raise RuntimeError("echoforge models_download.py " f"not found: {scriptPath}")

    # ----------------------------------------
    # Generic Hugging Face downloader
    # ----------------------------------------

    if scope == "generic" and downloaderName == GENERIC_HF_DOWNLOADER:

        command = [
            sys.executable,
            str(scriptPath),
            "--hf-repo",
            source,
            "--cache-name",
            resolvedCacheName,
        ]

    # ----------------------------------------
    # Existing model-specific downloader
    # ----------------------------------------

    elif scope == "model-specific":

        if modelListName:

            command = [
                sys.executable,
                str(scriptPath),
                "--name",
                (f"{downloaderName}:" f"{modelListName}"),
            ]

        else:

            command = [
                sys.executable,
                str(scriptPath),
                "--name",
                downloaderName,
            ]

    else:

        raise RuntimeError("Unsupported echoforge downloader: " f"{downloaderName}")

    # ----------------------------------------
    # Logging
    # ----------------------------------------

    print()
    print("[Onboarding] Starting " "echoforge download")

    print(f"[Onboarding] Model: " f"{modelName}")

    print(f"[Onboarding] Downloader: " f"{downloaderName}")

    if modelListName:

        print("[Onboarding] Model list name: " f"{modelListName}")

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
