import os
import subprocess
import sys

from app.services.echoforge.echoforgeConfig import (
    MODEL_DOWNLOAD_DIR,
    CACHE_DIR,
    ECHOFORGE_ROOT,
)


def getEchoForgeEnvironment() -> dict[str, str]:
    """
    Build environment for EchoForge subprocesses.

    Reads EchoForge's root .env so values such as
    HF_TOKEN are available to models_download.py.
    """

    env = os.environ.copy()

    envFile = ECHOFORGE_ROOT / ".env"

    if not envFile.exists():
        return env

    with envFile.open(
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            if line.startswith("#"):
                continue

            if "=" not in line:
                continue

            key, value = line.split(
                "=",
                1,
            )

            key = key.strip()
            value = value.strip()

            if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
                value = value[1:-1]

            if key not in env:
                env[key] = value

    return env


def downloadModel(
    downloader: dict,
    modelName: str,
    sourceType: str,
    source: str,
    cacheName: str | None = None,
) -> dict:

    downloaderName = downloader["downloader"]

    scope = downloader.get("scope")

    # Resolver may already know the exact cache
    # name from EchoForge model_info.json.
    resolvedCacheName = (
        downloader.get("cacheName")
        or cacheName
        or modelName.replace("/", "-").replace(" ", "-")
    )

    scriptPath = MODEL_DOWNLOAD_DIR / "models_download.py"

    if not scriptPath.exists():
        raise RuntimeError("EchoForge models_download.py " f"not found: {scriptPath}")

    # ----------------------------------------
    # Generic Hugging Face downloader
    # ----------------------------------------

    if scope == "generic" and downloaderName == "hugging_face_download":

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

        command = [
            sys.executable,
            str(scriptPath),
            "--name",
            downloaderName,
        ]

    else:

        raise RuntimeError("Unsupported EchoForge downloader: " f"{downloaderName}")

    print()
    print("[Onboarding] Starting EchoForge download")
    print(f"[Onboarding] Model: {modelName}")
    print(f"[Onboarding] Downloader: " f"{downloaderName}")
    print(f"[Onboarding] Cache name: " f"{resolvedCacheName}")

    env = getEchoForgeEnvironment()

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

            print(f"[EchoForge] {line}")

    returnCode = process.wait()

    if returnCode != 0:

        raise RuntimeError(
            "EchoForge model download failed." "\n\n" + "\n".join(outputLines)
        )

    cachePath = CACHE_DIR / resolvedCacheName

    if not cachePath.exists():

        raise RuntimeError(
            "EchoForge download completed, "
            "but expected cache was not found: "
            f"{cachePath}"
        )

    return {
        "modelName": modelName,
        "sourceType": sourceType,
        "source": source,
        "downloader": downloaderName,
        "cacheName": resolvedCacheName,
        "cachePath": str(cachePath),
        "status": "completed",
    }
