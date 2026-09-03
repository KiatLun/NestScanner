from pathlib import Path
import os

ECHOFORGE_ROOT = Path(
    os.getenv(
        "ECHOFORGE_ROOT",
        "/mnt/c/Users/AJ/Desktop/echoforge",
    )
)

MODEL_DOWNLOAD_DIR = ECHOFORGE_ROOT / "deployment" / "model_download"

MODEL_INFO_FILE = MODEL_DOWNLOAD_DIR / "model_info.json"

MODEL_UPLOAD_DIR = ECHOFORGE_ROOT / "deployment" / "models_upload"

CACHE_DIR = ECHOFORGE_ROOT / "deployment" / ".cache"

CLEARML_ENV_FILE = ECHOFORGE_ROOT / "services" / "clearml-agent" / "clearml.env"


def getEchoForgeEnvironment() -> dict[str, str]:
    """
    Build the environment passed to EchoForge subprocesses.

    Starts with NestScanner's current environment, then adds values
    from EchoForge's root .env file such as HF_TOKEN.
    """

    env = os.environ.copy()

    if not ECHOFORGE_ENV_FILE.exists():
        return env

    with ECHOFORGE_ENV_FILE.open(
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

            key, value = line.split("=", 1)

            key = key.strip()
            value = value.strip()

            if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
                value = value[1:-1]

            # Existing environment takes priority.
            if key not in env:
                env[key] = value

    return env
