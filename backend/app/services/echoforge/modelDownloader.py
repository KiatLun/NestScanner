import os
import subprocess
import sys

from app.services.echoforge.echoforgeConfig import (
    MODEL_DOWNLOAD_DIR,
    CACHE_DIR,
    ECHOFORGE_ROOT,
)


def getEchoforgeEnvironment() -> dict[str, str]:
    """
    Build environment for echoforge subprocesses.

    Reads echoforge's root .env so values such as
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

    scriptPath = MODEL_DOWNLOAD_DIR / "models_download.py"

    if not scriptPath.exists():

        raise RuntimeError("echoforge models_download.py " f"not found: {scriptPath}")

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

        # A model_list-backed specific
        # downloader needs the exact variant.
        if modelListName:

            command = [
                sys.executable,
                str(scriptPath),
                "--name",
                (f"{downloaderName}:" f"{modelListName}"),
            ]

        # Some model-specific downloaders may
        # have no model_list and therefore only
        # need the downloader folder name.
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
    # Environment
    # ----------------------------------------

    env = getEchoforgeEnvironment()

    # ----------------------------------------
    # Run echoforge
    # ----------------------------------------

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
        "cacheName": (resolvedCacheName),
        "cachePath": str(cachePath),
        "status": "completed",
    }
