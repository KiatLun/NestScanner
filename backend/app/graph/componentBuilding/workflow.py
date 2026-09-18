from app.graph.componentBuilding.inferenceComponentResolver import (
    resolveInferenceComponent,
)

from app.services.echoforge.dockerImageBuilder import (
    ensureDockerImage,
)

from app.services.echoforge.echoforgeConfig import (
    COMPONENTS_DIR,
    STT_EVALUATION_DIR,
    STT_EVALUATION_DOCKERFILE,
    STT_EVALUATION_IMAGE,
)


def buildEvaluationComponent() -> dict:

    return {
        "component": "stt_evaluation",
        "componentDir": str(STT_EVALUATION_DIR),
        "dockerfile": str(STT_EVALUATION_DOCKERFILE),
        "buildContext": str(COMPONENTS_DIR),
        "imageName": (STT_EVALUATION_IMAGE),
        "entryPoint": "/app/main.py",
    }


def runComponentBuildingWorkflow(
    modelName: str,
    source: str,
    forceBuild: bool = False,
) -> dict:

    print()
    print("=" * 60)
    print("[Component Building Workflow] " f"Starting: {modelName}")
    print("=" * 60)

    # ----------------------------------------
    # 1. Resolve inference component
    # ----------------------------------------

    try:

        inferenceComponent = resolveInferenceComponent(
            modelName=modelName,
            source=source,
        )

    except Exception as error:

        print(
            "[Component Building Workflow] "
            "Inference component resolution "
            f"failed: {error}"
        )

        return {
            "modelName": modelName,
            "source": source,
            "status": ("inference-component-resolution-failed"),
            "error": str(error),
        }

    # ----------------------------------------
    # 2. No inference component
    # ----------------------------------------

    if inferenceComponent is None:

        print(
            "[Component Building Workflow] "
            "No compatible inference "
            "component found."
        )

        return {
            "modelName": modelName,
            "source": source,
            "status": ("inference-component-required"),
            "inferenceComponent": None,
        }

    print(
        "[Component Building Workflow] "
        "Inference component: "
        f"{inferenceComponent['component']}"
    )

    # ----------------------------------------
    # 3. Build inference image if needed
    # ----------------------------------------

    try:

        inferenceImageResult = ensureDockerImage(
            imageName=(inferenceComponent["imageName"]),
            dockerfile=(inferenceComponent["dockerfile"]),
            buildContext=(inferenceComponent["buildContext"]),
            forceBuild=forceBuild,
        )

    except Exception as error:

        print(
            "[Component Building Workflow] "
            "Inference image preparation "
            f"failed: {error}"
        )

        return {
            "modelName": modelName,
            "source": source,
            "status": ("inference-image-build-failed"),
            "inferenceComponent": (inferenceComponent),
            "error": str(error),
        }

    print(
        "[Component Building Workflow] "
        "Inference image: "
        f"{inferenceComponent['imageName']}"
    )

    print(
        "[Component Building Workflow] "
        "Inference image status: "
        f"{inferenceImageResult['status']}"
    )

    # ----------------------------------------
    # 4. Resolve evaluation component
    # ----------------------------------------

    evaluationComponent = buildEvaluationComponent()

    print(
        "[Component Building Workflow] "
        "Evaluation component: "
        f"{evaluationComponent['component']}"
    )

    # ----------------------------------------
    # 5. Build evaluation image if needed
    # ----------------------------------------

    try:

        evaluationImageResult = ensureDockerImage(
            imageName=(evaluationComponent["imageName"]),
            dockerfile=(evaluationComponent["dockerfile"]),
            buildContext=(evaluationComponent["buildContext"]),
            forceBuild=forceBuild,
        )

    except Exception as error:

        print(
            "[Component Building Workflow] "
            "Evaluation image preparation "
            f"failed: {error}"
        )

        return {
            "modelName": modelName,
            "source": source,
            "status": ("evaluation-image-build-failed"),
            "inferenceComponent": (inferenceComponent),
            "inferenceImageResult": (inferenceImageResult),
            "evaluationComponent": (evaluationComponent),
            "error": str(error),
        }

    print(
        "[Component Building Workflow] "
        "Evaluation image: "
        f"{evaluationComponent['imageName']}"
    )

    print(
        "[Component Building Workflow] "
        "Evaluation image status: "
        f"{evaluationImageResult['status']}"
    )

    # ----------------------------------------
    # 6. Completed
    # ----------------------------------------

    result = {
        "modelName": modelName,
        "source": source,
        "status": "completed",
        "inferenceComponent": (inferenceComponent),
        "inferenceImageResult": (inferenceImageResult),
        "evaluationComponent": (evaluationComponent),
        "evaluationImageResult": (evaluationImageResult),
    }

    print("[Component Building Workflow] " f"Completed: {modelName}")

    return result
