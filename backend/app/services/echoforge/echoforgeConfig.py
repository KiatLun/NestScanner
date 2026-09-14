from pathlib import Path
import os


def getRequiredPath(
    environmentVariable: str,
) -> Path:

    value = os.getenv(environmentVariable)

    if not value:
        raise RuntimeError(
            f"Missing required environment variable: " f"{environmentVariable}"
        )

    return Path(value).expanduser().resolve()


# ----------------------------------------
# echoforge root
# ----------------------------------------

ECHOFORGE_ROOT = getRequiredPath("ECHOFORGE_ROOT")


# ----------------------------------------
# echoforge paths
# ----------------------------------------

DEPLOYMENT_DIR = ECHOFORGE_ROOT / "deployment"

MODEL_DOWNLOAD_DIR = DEPLOYMENT_DIR / "model_download"

MODEL_UPLOAD_DIR = DEPLOYMENT_DIR / "models_upload"

MODEL_INFO_FILE = MODEL_DOWNLOAD_DIR / "model_info.json"

CACHE_DIR = DEPLOYMENT_DIR / ".cache"

CLEARML_ENV_FILE = ECHOFORGE_ROOT / "services" / "clearml-agent" / "clearml.env"

ECHOFORGE_ENV_FILE = ECHOFORGE_ROOT / ".env"


def getEchoforgeEnvironment() -> dict[str, str]:
    """
    Build the environment passed to echoforge subprocesses.

    Starts with NestScanner's current environment and supplements it
    with values from echoforge's root .env file.
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

            key, value = line.split(
                "=",
                1,
            )

            key = key.strip()
            value = value.strip()

            if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
                value = value[1:-1]

            # NestScanner environment takes priority.
            if key not in env:
                env[key] = value

    return env
