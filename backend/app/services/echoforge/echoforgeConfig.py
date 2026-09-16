from pathlib import Path
import os

from dotenv import load_dotenv

# ----------------------------------------
# NestScanner root
# ----------------------------------------

NESTSCANNER_ROOT = Path(__file__).resolve().parents[3]


# ----------------------------------------
# Load NestScanner .env
# ----------------------------------------

NESTSCANNER_ENV_FILE = NESTSCANNER_ROOT / ".env"

load_dotenv(NESTSCANNER_ENV_FILE)


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
# NestScanner data paths
# ----------------------------------------

DATA_DIR = NESTSCANNER_ROOT / "data"

ECHOFORGE_DATA_DIR = DATA_DIR / "echoforge"

MODEL_INFO_FILE = ECHOFORGE_DATA_DIR / "model_info.json"


# ----------------------------------------
# echoforge root
# ----------------------------------------

ECHOFORGE_ROOT = getRequiredPath("ECHOFORGE_ROOT")


# ----------------------------------------
# echoforge deployment paths
# ----------------------------------------

DEPLOYMENT_DIR = ECHOFORGE_ROOT / "deployment"

MODEL_DOWNLOAD_DIR = DEPLOYMENT_DIR / "model_download"

MODEL_UPLOAD_DIR = DEPLOYMENT_DIR / "models_upload"

CACHE_DIR = DEPLOYMENT_DIR / ".cache"


# ----------------------------------------
# echoforge component paths
# ----------------------------------------

COMPONENTS_DIR = ECHOFORGE_ROOT / "components"

INFERENCE_COMPONENT_DIR = COMPONENTS_DIR / "inference_component"

STT_INFERENCE_DIR = INFERENCE_COMPONENT_DIR / "stt_inference"

EVALUATION_COMPONENT_DIR = COMPONENTS_DIR / "evaluation_component"

STT_EVALUATION_DIR = EVALUATION_COMPONENT_DIR / "stt_evaluation"

STT_EVALUATION_FILE = STT_EVALUATION_DIR / "main.py"


# ----------------------------------------
# echoforge pipeline paths
# ----------------------------------------

PIPELINE_DIR = COMPONENTS_DIR / "pipeline"

PIPELINE_SRC_DIR = PIPELINE_DIR / "src"

PIPELINE_CONF_DIR = PIPELINE_SRC_DIR / "conf"

PIPELINE_MAIN_FILE = PIPELINE_SRC_DIR / "main.py"

NESTSCANNER_PIPELINE_CONF_DIR = PIPELINE_CONF_DIR / "nestscanner"

# ----------------------------------------
# echoforge environment paths
# ----------------------------------------

CLEARML_ENV_FILE = ECHOFORGE_ROOT / "services" / "clearml-agent" / "clearml.env"

ECHOFORGE_ENV_FILE = ECHOFORGE_ROOT / ".env"


# ----------------------------------------
# echoforge environment
# ----------------------------------------


def getEchoforgeEnvironment() -> dict[str, str]:
    """
    Build the environment passed to echoforge subprocesses.

    Starts with NestScanner's current environment
    and supplements it with values from echoforge's
    root .env file.
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

            if key not in env:
                env[key] = value

    return env
