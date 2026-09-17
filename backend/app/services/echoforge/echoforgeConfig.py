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
            "Missing required environment " f"variable: {environmentVariable}"
        )

    return Path(value).expanduser().resolve()


# ----------------------------------------
# NestScanner data paths
# ----------------------------------------

DATA_DIR = NESTSCANNER_ROOT / "data"

ECHOFORGE_DATA_DIR = DATA_DIR / "echoforge"

MODEL_INFO_FILE = ECHOFORGE_DATA_DIR / "model_info.json"


# ----------------------------------------
# EchoForge root
# ----------------------------------------

ECHOFORGE_ROOT = getRequiredPath("ECHOFORGE_ROOT")


# ----------------------------------------
# EchoForge deployment paths
# ----------------------------------------

DEPLOYMENT_DIR = ECHOFORGE_ROOT / "deployment"

MODEL_DOWNLOAD_DIR = DEPLOYMENT_DIR / "model_download"

MODEL_UPLOAD_DIR = DEPLOYMENT_DIR / "models_upload"

CACHE_DIR = DEPLOYMENT_DIR / ".cache"


# ----------------------------------------
# EchoForge component paths
# ----------------------------------------

COMPONENTS_DIR = ECHOFORGE_ROOT / "components"

INFERENCE_COMPONENT_DIR = COMPONENTS_DIR / "inference_component"

STT_INFERENCE_DIR = INFERENCE_COMPONENT_DIR / "stt_inference"

EVALUATION_COMPONENT_DIR = COMPONENTS_DIR / "evaluation_component"

STT_EVALUATION_DIR = EVALUATION_COMPONENT_DIR / "stt_evaluation"

STT_EVALUATION_FILE = STT_EVALUATION_DIR / "main.py"


# ----------------------------------------
# EchoForge pipeline paths
# ----------------------------------------

PIPELINE_DIR = ECHOFORGE_ROOT / "pipeline"

PIPELINE_SRC_DIR = PIPELINE_DIR / "src"

PIPELINE_CONF_DIR = PIPELINE_SRC_DIR / "conf"

NESTSCANNER_PIPELINE_CONF_DIR = PIPELINE_CONF_DIR / "nestscanner"

PIPELINE_MAIN_FILE = PIPELINE_SRC_DIR / "main.py"


# ----------------------------------------
# NestScanner EchoForge runtime
# ----------------------------------------

NESTSCANNER_EVALUATION_IMAGE = "nestscanner_evaluation:latest"


# ----------------------------------------
# EchoForge ClearML paths
# ----------------------------------------

CLEARML_AGENT_DIR = ECHOFORGE_ROOT / "services" / "clearml-agent"

CLEARML_ENV_FILE = CLEARML_AGENT_DIR / "clearml.env"

CLEARML_CONFIG_FILE = CLEARML_AGENT_DIR / "clearml.conf"


# ----------------------------------------
# EchoForge environment paths
# ----------------------------------------

ECHOFORGE_ENV_FILE = ECHOFORGE_ROOT / ".env"


# ----------------------------------------
# EchoForge Docker deployment paths
# ----------------------------------------

DOCKER_DEPLOYMENT_DIR = DEPLOYMENT_DIR / "docker"

IMAGE_DOWNLOADER_DIR = DOCKER_DEPLOYMENT_DIR / "image_downloader"

IMAGE_BUILDER_FILE = IMAGE_DOWNLOADER_DIR / "image_builder_and_downloader.py"


# ----------------------------------------
# EchoForge environment
# ----------------------------------------


def getEchoforgeEnvironment() -> dict[str, str]:
    """
    Build the environment passed to EchoForge
    subprocesses.

    Starts with NestScanner's current environment
    and supplements it with values from EchoForge's
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
