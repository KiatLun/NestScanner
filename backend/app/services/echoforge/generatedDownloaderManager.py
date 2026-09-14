import subprocess
import sys
from pathlib import Path

from app.services.echoforge.echoforgeConfig import (
    CACHE_DIR,
    MODEL_DOWNLOAD_DIR,
    getEchoforgeEnvironment,
)

ALLOWED_FILES = {
    "download.py",
    "dockerfile",
    "model_list",
}


def validateDownloaderFiles(
    files: dict,
) -> None:

    if not isinstance(files, dict):
        raise ValueError("Generated downloader files must be a dictionary.")

    providedFiles = set(files.keys())

    if providedFiles != ALLOWED_FILES:
        raise ValueError(
            "Generated downloader must contain exactly: "
            "download.py, dockerfile, model_list"
        )

    for fileName, content in files.items():

        if not isinstance(content, str):
            raise ValueError(f"{fileName} must contain text.")

        if not content.strip():
            raise ValueError(f"{fileName} cannot be empty.")


def getDownloaderPath(
    downloaderName: str,
) -> Path:

    if "/" in downloaderName or "\\" in downloaderName:
        raise ValueError("Invalid downloader name.")

    if ".." in downloaderName:
        raise ValueError("Invalid downloader name.")

    return MODEL_DOWNLOAD_DIR / downloaderName


def writeDownloaderFiles(
    downloaderName: str,
    files: dict,
    allowOverwrite: bool = False,
) -> Path:

    validateDownloaderFiles(files)

    downloaderPath = getDownloaderPath(downloaderName)

    if downloaderPath.exists() and not allowOverwrite:
        raise RuntimeError("Downloader directory already exists: " f"{downloaderPath}")

    downloaderPath.mkdir(
        parents=False,
        exist_ok=True,
    )

    for fileName, content in files.items():

        filePath = downloaderPath / fileName

        filePath.write_text(
            content,
            encoding="utf-8",
        )

    return downloaderPath


def runGeneratedDownloader(
    downloaderName: str,
    modelListName: str,
    cacheName: str,
) -> dict:

    scriptPath = MODEL_DOWNLOAD_DIR / "models_download.py"

    if not scriptPath.exists():

        raise RuntimeError("echoforge models_download.py " f"not found: {scriptPath}")

    command = [
        sys.executable,
        str(scriptPath),
        "--name",
        (f"{downloaderName}:" f"{modelListName}"),
        "--force",
    ]

    env = getEchoforgeEnvironment()

    print()
    print("[Downloader Builder] " "Testing generated downloader")

    print("[Downloader Builder] Command: " + " ".join(command))

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

    cachePath = CACHE_DIR / cacheName

    cacheValid = cachePath.exists() and cachePath.is_dir() and any(cachePath.iterdir())

    success = returnCode == 0 and cacheValid

    return {
        "success": success,
        "returnCode": returnCode,
        "cacheName": cacheName,
        "cachePath": str(cachePath),
        "cacheValid": cacheValid,
        "output": "\n".join(outputLines),
    }
