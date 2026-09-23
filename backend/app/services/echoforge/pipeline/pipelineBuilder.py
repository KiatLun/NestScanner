import yaml

from app.services.echoforge.echoforgeConfig import (
    NESTSCANNER_PIPELINE_CONF_DIR,
)

QUEUE_NAME = "echoforge_queue"


def normalizeName(
    value: str,
) -> str:

    return value.strip().lower().replace("-", "_").replace(" ", "_")


def validateComponent(
    component: dict,
    componentType: str,
) -> None:

    componentName = component.get("component")

    imageName = component.get("imageName")

    entryPoint = component.get("entryPoint")

    if not componentName:
        raise RuntimeError(f"{componentType} component " "name is missing.")

    if not imageName:
        raise RuntimeError(
            f"{componentType} component "
            "imageName is missing for "
            f"component: {componentName}"
        )

    if not entryPoint:
        raise RuntimeError(
            f"{componentType} component "
            "entryPoint is missing for "
            f"component: {componentName}"
        )


def buildEvaluationPipeline(
    modelName: str,
    modelId: str,
    datasetId: str,
    inferenceComponent: dict,
    evaluationComponent: dict,
) -> dict:

    if not modelId:
        raise RuntimeError("Model ID is required.")

    if not datasetId:
        raise RuntimeError("Dataset ID is required.")

    validateComponent(
        inferenceComponent,
        "Inference",
    )

    validateComponent(
        evaluationComponent,
        "Evaluation",
    )

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
                "image_name": (inferenceComponent["imageName"]),
                "task_type": "inference",
                "entry_point": (inferenceComponent["entryPoint"]),
                "cache_executed_step": False,
                "parameter_override": {
                    "Args/dataset_id": ("${datasets}"),
                    "Args/model_id": (modelId),
                },
            },
            evaluationStageName: {
                "queue": QUEUE_NAME,
                "image_name": (evaluationComponent["imageName"]),
                "task_type": "testing",
                "entry_point": (evaluationComponent["entryPoint"]),
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
