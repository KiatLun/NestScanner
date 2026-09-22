from app.graph.componentBuilding.inferenceComponentResolver import (
    resolveInferenceComponent,
)

from app.agents.componentCreation.agent import (
    componentCreationAgent,
)

from app.agents.componentCreation.implementationResearch import (
    researchModelImplementation,
)

from app.agents.componentCreation.schemas import (
    ComponentCreationInput,
)

from app.services.echoforge.componentWriter import (
    writeGeneratedComponent,
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
        "imageName": STT_EVALUATION_IMAGE,
        "entryPoint": "/app/main.py",
    }


def createInferenceComponent(
    modelName: str,
    source: str,
    modelFamily: str,
    technicalProfile: dict,
) -> tuple[dict, dict]:

    # ----------------------------------------
    # 1. Research model implementation
    # ----------------------------------------

    print(
        "[Component Building Workflow] "
        "Researching target-model implementation."
    )

    implementationResearchResult = (
        researchModelImplementation(
            modelName=modelName,
            modelFamily=modelFamily,
            source=source,
            technicalProfile=technicalProfile,
        )
    )

    implementationResearchStatus = (
        implementationResearchResult.get(
            "status"
        )
    )

    if (
        implementationResearchStatus
        != "completed"
    ):

        raise RuntimeError(
            "Model implementation research "
            "did not produce sufficient "
            "implementation evidence. "
            f"Status: "
            f"{implementationResearchStatus}"
        )

    implementationContext = (
        implementationResearchResult.get(
            "implementationContext",
            "",
        )
    )

    if not implementationContext.strip():

        raise RuntimeError(
            "Model implementation research "
            "returned an empty "
            "implementationContext."
        )

    print(
        "[Component Building Workflow] "
        "Implementation research completed."
    )

    # ----------------------------------------
    # 2. Generate EchoForge component
    # ----------------------------------------

    print(
        "[Component Building Workflow] "
        "Calling Component Creation Agent."
    )

    creationInput = (
        ComponentCreationInput(
            modelName=modelName,
            modelFamily=modelFamily,
            source=source,
            technicalProfile=technicalProfile,
            implementationContext=(
                implementationContext
            ),
        )
    )

    generatedComponent = (
        componentCreationAgent(
            creationInput
        )
    )

    print(
        "[Component Building Workflow] "
        "Component generated: "
        f"{generatedComponent.componentName}"
    )

    # ----------------------------------------
    # 3. Write generated files
    # ----------------------------------------

    componentFiles = (
        writeGeneratedComponent(
            componentName=(
                generatedComponent.componentName
            ),
            mainFileContent=(
                generatedComponent.mainFileContent
            ),
            requirementsContent=(
                generatedComponent.requirementsContent
            ),
            dockerfileContent=(
                generatedComponent.dockerfileContent
            ),
        )
    )

    inferenceComponent = {
        **componentFiles,
        "family": modelFamily,
        "imageName": (
            generatedComponent.imageName
        ),
        "entryPoint": (
            generatedComponent.entryPoint
        ),
        "modelName": modelName,
        "source": source,
        "matchedBy": "generated",
    }

    return (
        inferenceComponent,
        implementationResearchResult,
    )


def runComponentBuildingWorkflow(
    modelName: str,
    source: str,
    modelFamily: str,
    technicalProfile: dict | None = None,
    forceBuild: bool = False,
) -> dict:

    technicalProfile = (
        technicalProfile
        or {}
    )

    implementationResearchResult = None

    print()
    print("=" * 60)

    print(
        "[Component Building Workflow] "
        f"Starting: {modelName}"
    )

    print("=" * 60)

    # ----------------------------------------
    # 1. Resolve inference component
    # ----------------------------------------

    try:

        inferenceComponent = (
            resolveInferenceComponent(
                modelName=modelName,
                source=source,
            )
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
            "status": (
                "inference-component-resolution-failed"
            ),
            "error": str(error),
        }

    # ----------------------------------------
    # 2. Research + create if none exists
    # ----------------------------------------

    if inferenceComponent is None:

        print(
            "[Component Building Workflow] "
            "No compatible inference "
            "component found."
        )

        try:

            (
                inferenceComponent,
                implementationResearchResult,
            ) = createInferenceComponent(
                modelName=modelName,
                source=source,
                modelFamily=modelFamily,
                technicalProfile=(
                    technicalProfile
                ),
            )

        except Exception as error:

            print(
                "[Component Building Workflow] "
                "Component creation failed: "
                f"{error}"
            )

            return {
                "modelName": modelName,
                "source": source,
                "status": (
                    "inference-component-creation-failed"
                ),
                "implementationResearchResult": (
                    implementationResearchResult
                ),
                "error": str(error),
            }

    else:

        print(
            "[Component Building Workflow] "
            "Using existing inference component."
        )

    print(
        "[Component Building Workflow] "
        "Inference component: "
        f"{inferenceComponent['component']}"
    )

    print(
        "[Component Building Workflow] "
        "Component source: "
        f"{inferenceComponent['matchedBy']}"
    )

    # ----------------------------------------
    # 3. Build inference image if needed
    # ----------------------------------------

    try:

        inferenceImageResult = (
            ensureDockerImage(
                imageName=(
                    inferenceComponent[
                        "imageName"
                    ]
                ),
                dockerfile=(
                    inferenceComponent[
                        "dockerfile"
                    ]
                ),
                buildContext=(
                    inferenceComponent[
                        "buildContext"
                    ]
                ),
                forceBuild=forceBuild,
            )
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
            "status": (
                "inference-image-build-failed"
            ),
            "inferenceComponent": (
                inferenceComponent
            ),
            "implementationResearchResult": (
                implementationResearchResult
            ),
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

    evaluationComponent = (
        buildEvaluationComponent()
    )

    print(
        "[Component Building Workflow] "
        "Evaluation component: "
        f"{evaluationComponent['component']}"
    )

    # ----------------------------------------
    # 5. Build evaluation image if needed
    # ----------------------------------------

    try:

        evaluationImageResult = (
            ensureDockerImage(
                imageName=(
                    evaluationComponent[
                        "imageName"
                    ]
                ),
                dockerfile=(
                    evaluationComponent[
                        "dockerfile"
                    ]
                ),
                buildContext=(
                    evaluationComponent[
                        "buildContext"
                    ]
                ),
                forceBuild=False, # to set it back to flag
            )
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
            "status": (
                "evaluation-image-build-failed"
            ),
            "inferenceComponent": (
                inferenceComponent
            ),
            "inferenceImageResult": (
                inferenceImageResult
            ),
            "evaluationComponent": (
                evaluationComponent
            ),
            "implementationResearchResult": (
                implementationResearchResult
            ),
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
        "inferenceComponent": (
            inferenceComponent
        ),
        "inferenceImageResult": (
            inferenceImageResult
        ),
        "evaluationComponent": (
            evaluationComponent
        ),
        "evaluationImageResult": (
            evaluationImageResult
        ),
    }

    if (
        implementationResearchResult
        is not None
    ):

        result[
            "implementationResearchResult"
        ] = implementationResearchResult

    print(
        "[Component Building Workflow] "
        f"Completed: {modelName}"
    )

    return result