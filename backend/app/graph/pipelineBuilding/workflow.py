from app.services.echoforge.pipeline.pipelineBuilder import (
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
            "status": "component-building-incomplete",
            "componentStatus": componentResult.get("status"),
            "generatedFiles": [],
        }

    inferenceComponent = componentResult.get("inferenceComponent")

    evaluationComponent = componentResult.get("evaluationComponent")

    if not inferenceComponent:

        return {
            "modelName": modelName,
            "status": "inference-component-missing",
            "generatedFiles": [],
        }

    if not evaluationComponent:

        return {
            "modelName": modelName,
            "status": "evaluation-component-missing",
            "generatedFiles": [],
        }

    # ----------------------------------------
    # 2. Build pipeline config
    # ----------------------------------------

    try:

        pipeline = buildEvaluationPipeline(
            modelName=modelName,
            modelId=modelId,
            datasetId=datasetId,
            inferenceComponent=inferenceComponent,
            evaluationComponent=evaluationComponent,
        )

    except Exception as error:

        print(
            "[Pipeline Building Workflow] "
            "Pipeline configuration build "
            f"failed: {error}"
        )

        return {
            "modelName": modelName,
            "status": "pipeline-build-failed",
            "generatedFiles": [],
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
            "status": "pipeline-write-failed",
            "pipeline": pipeline,
            "generatedFiles": [],
            "error": str(error),
        }

    print(
        "[Pipeline Building Workflow] "
        "Pipeline file: "
        f"{pipelineFileResult['pipelinePath']}"
    )

    # ----------------------------------------
    # 4. Record generated files for GitHub PR
    # ----------------------------------------

    generatedFiles = pipelineFileResult.get(
        "generatedFiles",
        [],
    )

    print(
        "[Pipeline Building Workflow] "
        f"Recorded {len(generatedFiles)} "
        "generated files for GitHub PR."
    )

    # ----------------------------------------
    # 5. Completed
    # ----------------------------------------

    result = {
        "modelName": modelName,
        "modelId": modelId,
        "datasetId": datasetId,
        "status": "completed",
        "pipeline": pipeline,
        "pipelineName": pipelineFileResult["pipelineName"],
        "pipelinePath": pipelineFileResult["pipelinePath"],
        "generatedFiles": generatedFiles,
    }

    print("[Pipeline Building Workflow] " f"Completed: {modelName}")

    return result
