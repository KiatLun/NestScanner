from app.services.echoforge.pipelineBuilder import (
    buildEvaluationPipeline,
    writeEvaluationPipeline,
)


def runPipelineBuildingWorkflow(
    modelName: str,
    modelId: str,
    datasetId: str,
    componentResult: dict,
) -> dict:

    print()
    print("=" * 60)
    print("[Pipeline Building Workflow] " f"Starting: {modelName}")
    print("=" * 60)

    # ----------------------------------------
    # 1. Validate component building result
    # ----------------------------------------

    if componentResult.get("status") != "completed":
        return {
            "modelName": modelName,
            "status": ("component-building-incomplete"),
            "componentStatus": (componentResult.get("status")),
        }

    inferenceComponent = componentResult.get("inferenceComponent")

    evaluationComponent = componentResult.get("evaluationComponent")

    if not inferenceComponent:

        return {
            "modelName": modelName,
            "status": ("inference-component-missing"),
        }

    if not evaluationComponent:

        return {
            "modelName": modelName,
            "status": ("evaluation-component-missing"),
        }

    # ----------------------------------------
    # 2. Build pipeline config
    # ----------------------------------------

    try:

        pipeline = buildEvaluationPipeline(
            modelName=modelName,
            modelId=modelId,
            datasetId=datasetId,
            inferenceComponent=(inferenceComponent),
            evaluationComponent=(evaluationComponent),
        )

    except Exception as error:

        print(
            "[Pipeline Building Workflow] "
            "Pipeline configuration build "
            f"failed: {error}"
        )

        return {
            "modelName": modelName,
            "status": ("pipeline-build-failed"),
            "error": str(error),
        }

    print("[Pipeline Building Workflow] " "Pipeline configuration created.")

    # ----------------------------------------
    # 3. Write pipeline YAML
    # ----------------------------------------

    try:

        pipelineFileResult = writeEvaluationPipeline(
            modelName=modelName,
            pipeline=pipeline,
        )

    except Exception as error:

        print("[Pipeline Building Workflow] " "Pipeline YAML write failed: " f"{error}")

        return {
            "modelName": modelName,
            "status": ("pipeline-write-failed"),
            "pipeline": pipeline,
            "error": str(error),
        }

    print(
        "[Pipeline Building Workflow] "
        "Pipeline file: "
        f"{pipelineFileResult['pipelinePath']}"
    )

    # ----------------------------------------
    # 4. Completed
    # ----------------------------------------

    result = {
        "modelName": modelName,
        "modelId": modelId,
        "datasetId": datasetId,
        "status": "completed",
        "pipeline": pipeline,
        "pipelineName": (pipelineFileResult["pipelineName"]),
        "pipelinePath": (pipelineFileResult["pipelinePath"]),
    }

    print("[Pipeline Building Workflow] " f"Completed: {modelName}")

    return result
