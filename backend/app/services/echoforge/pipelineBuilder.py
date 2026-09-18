import yaml

from app.services.echoforge.echoforgeConfig import (
    NESTSCANNER_PIPELINE_CONF_DIR,
    STT_EVALUATION_IMAGE,
)

QUEUE_NAME = "echoforge_queue"


def normalizeName(
    value: str,
) -> str:

    return value.strip().lower().replace("-", "_").replace(" ", "_")


def getEvaluationEntryPoint() -> str:

    return "/app/main.py"


def buildEvaluationPipeline(
    modelName: str,
    modelId: str,
    datasetId: str,
    component: dict,
) -> dict:

    componentName = component.get("component")

    imageName = component.get("imageName")

    entryPoint = component.get("entryPoint")

    if not componentName:
        raise RuntimeError("Inference component name is missing.")

    if not imageName:
        raise RuntimeError(
            "Inference component imageName "
            f"is missing for component: "
            f"{componentName}"
        )

    if not entryPoint:
        raise RuntimeError(
            "Inference component entryPoint "
            f"is missing for component: "
            f"{componentName}"
        )

    if not modelId:
        raise RuntimeError("Model ID is required.")

    if not datasetId:
        raise RuntimeError("Dataset ID is required.")

    inferenceStageName = "stt_inference"

    evaluationStageName = "stt_evaluation"

    return {
        "project_name": (f"nestscanner_" f"{normalizeName(modelName)}"),
        "datasets": {
            "dataset_ids": [
                datasetId,
            ],
            "tags": [],
            "exclude_tags": [],
        },
        "stages": {
            inferenceStageName: {
                "queue": QUEUE_NAME,
                "image_name": imageName,
                "task_type": "inference",
                "entry_point": entryPoint,
                "cache_executed_step": False,
                "parameter_override": {
                    "Args/dataset_id": ("${datasets}"),
                    "Args/model_id": (modelId),
                },
            },
            evaluationStageName: {
                "queue": QUEUE_NAME,
                "image_name": (STT_EVALUATION_IMAGE),
                "task_type": "testing",
                "entry_point": (getEvaluationEntryPoint()),
                "cache_executed_step": False,
                "parents": [
                    inferenceStageName,
                ],
                "parameter_override": {
                    "Args/hyp_dataset_id": (
                        f"${{{inferenceStageName}.id}}:" "dataset_id"
                    ),
                    "Args/ref_dataset_id": ("${datasets}"),
                },
            },
        },
    }


def writeEvaluationPipeline(
    modelName: str,
    pipeline: dict,
) -> dict:

    NESTSCANNER_PIPELINE_CONF_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    pipelineName = f"{normalizeName(modelName)}" "_evaluation.yaml"

    pipelinePath = NESTSCANNER_PIPELINE_CONF_DIR / pipelineName

    pipelinePath.write_text(
        yaml.safe_dump(
            pipeline,
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    return {
        "pipelineName": pipelineName,
        "pipelinePath": str(pipelinePath),
    }
