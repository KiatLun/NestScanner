import subprocess
from pathlib import Path

ECHOFORGE_PATH = Path("/mnt/c/Users/AJ/Desktop/echoforge")


def downloadHuggingFaceModel(
    repoId: str,
    cacheName: str,
) -> dict:

    modelDownloadPath = ECHOFORGE_PATH / "deployment" / "model_download"

    scriptPath = modelDownloadPath / "models_download.py"

    if not scriptPath.exists():
        raise FileNotFoundError(f"EchoForge downloader not found: " f"{scriptPath}")

    command = [
        "python",
        "models_download.py",
        "--hf-repo",
        repoId,
        "--cache-name",
        cacheName,
    ]

    print("\n=== ECHOFORGE MODEL DOWNLOAD ===")

    print(f"Repository: {repoId}")

    print(f"Cache name: {cacheName}")

    result = subprocess.run(
        command,
        cwd=modelDownloadPath,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError("EchoForge model download failed.")

    cachePath = ECHOFORGE_PATH / "deployment" / ".cache" / cacheName

    if not cachePath.exists():
        raise RuntimeError(
            "EchoForge download completed but " f"cache was not found at {cachePath}"
        )

    return {
        "repoId": repoId,
        "cacheName": cacheName,
        "cachePath": str(cachePath),
        "status": "completed",
    }
