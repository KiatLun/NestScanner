from pprint import pprint

from app.graph.componentBuilding.workflow import (
    runComponentBuildingWorkflow,
)

from app.graph.pipelineBuilding.workflow import (
    runPipelineBuildingWorkflow,
)

from app.services.echoforge.pipelineRunner import (
    runPipeline,
)

from tests.fixtures.researchAgentOutput import (
    researchAgentOutput,
)


# ============================================================
# Models to test
# ============================================================

modelsToTest = [
    # "qwen3-asr-1.7b",
    "sensevoice-small",
    # "whisper-small",
]


# ============================================================
# Model test configuration
# ============================================================

modelTestConfig = {

    "qwen3-asr-1.7b": {
        "modelFamily": "qwen",
        "modelId": "YOUR_QWEN_MODEL_ID",
    },

    "sensevoice-small": {
        "modelFamily": "sensevoice",
        "modelId": "eb2929f468464fe387333e0bb379dbd6",
    },

    "whisper-small": {
        "modelFamily": "whisper",
        "modelId": "89ad20fe7b044a7e90774afae8f44ba9",
    },
}


# ============================================================
# Dataset
# ============================================================

# Windows / WSL
# DATASET_ID = "b68dd036d6514d68822f717fd52c99ee"

# Mac
DATASET_ID = "30ab6615fd76498ab8642e104575d205"


# ============================================================
# Helpers
# ============================================================

def printSection(
    title: str,
):

    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


# ============================================================
# Run model test
# ============================================================

def runModelTest(
    modelKey: str,
):

    printSection(
        f"PIPELINE TEST: {modelKey}"
    )

    # --------------------------------------------------------
    # Validate fixtures
    # --------------------------------------------------------

    if (
        modelKey
        not in researchAgentOutput
    ):

        raise RuntimeError(
            "Research fixture not found: "
            f"{modelKey}"
        )

    if (
        modelKey
        not in modelTestConfig
    ):

        raise RuntimeError(
            "Model test config not found: "
            f"{modelKey}"
        )

    # --------------------------------------------------------
    # Get research result
    # --------------------------------------------------------

    researchResult = (
        researchAgentOutput[
            modelKey
        ]
    )

    testConfig = (
        modelTestConfig[
            modelKey
        ]
    )

    candidate = (
        researchResult[
            "candidate"
        ]
    )

    modelName = (
        candidate[
            "name"
        ]
    )

    source = (
        candidate[
            "sourceUrl"
        ]
    )

    modelFamily = (
        testConfig[
            "modelFamily"
        ]
    )

    modelId = (
        testConfig[
            "modelId"
        ]
    )

    technicalProfile = {
        "candidate": candidate,
        "isLocallyDeployable": (
            researchResult[
                "isLocallyDeployable"
            ]
        ),
        "researchEvidence": (
            researchResult[
                "researchEvidence"
            ]
        ),
    }

    print(
        f"Model: {modelName}"
    )

    print(
        f"Family: {modelFamily}"
    )

    print(
        f"Source: {source}"
    )

    print(
        f"Model ID: {modelId}"
    )

    print(
        f"Dataset ID: {DATASET_ID}"
    )

    # --------------------------------------------------------
    # 1. Component building
    # --------------------------------------------------------

    componentResult = (
        runComponentBuildingWorkflow(
            modelName=modelName,
            source=source,
            modelFamily=modelFamily,
            technicalProfile=(
                technicalProfile
            ),
            forceBuild=False,
        )
    )

    printSection(
        "COMPONENT BUILDING RESULT"
    )

    pprint(
        componentResult,
        sort_dicts=False,
    )

    if (
        componentResult.get(
            "status"
        )
        != "completed"
    ):

        raise RuntimeError(
            "Component Building failed.\n"
            f"Status: "
            f"{componentResult.get('status')}\n"
            f"Error: "
            f"{componentResult.get('error')}"
        )

    # --------------------------------------------------------
    # 2. Pipeline building
    # --------------------------------------------------------

    pipelineResult = (
        runPipelineBuildingWorkflow(
            modelName=modelName,
            modelId=modelId,
            datasetId=DATASET_ID,
            componentResult=(
                componentResult
            ),
        )
    )

    printSection(
        "PIPELINE BUILDING RESULT"
    )

    pprint(
        pipelineResult,
        sort_dicts=False,
    )

    if (
        pipelineResult.get(
            "status"
        )
        != "completed"
    ):

        raise RuntimeError(
            "Pipeline Building failed.\n"
            f"Status: "
            f"{pipelineResult.get('status')}\n"
            f"Error: "
            f"{pipelineResult.get('error')}"
        )

    # --------------------------------------------------------
    # 3. Pipeline running
    # --------------------------------------------------------

    runResult = runPipeline(
        pipelineResult[
            "pipelinePath"
        ]
    )

    printSection(
        "PIPELINE RUN RESULT"
    )

    pprint(
        runResult,
        sort_dicts=False,
    )

    return {
        "componentResult": (
            componentResult
        ),
        "pipelineResult": (
            pipelineResult
        ),
        "runResult": (
            runResult
        ),
    }


# ============================================================
# Main
# ============================================================

def main():

    printSection(
        "END-TO-END PIPELINE TEST"
    )

    passedModels = []
    failedModels = []

    for modelKey in (
        modelsToTest
    ):

        try:

            runModelTest(
                modelKey
            )

            passedModels.append(
                modelKey
            )

        except Exception as error:

            failedModels.append(
                {
                    "model": modelKey,
                    "error": str(
                        error
                    ),
                }
            )

            printSection(
                f"TEST FAILED: "
                f"{modelKey}"
            )

            print(
                str(
                    error
                )
            )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    printSection(
        "TEST SUMMARY"
    )

    print(
        f"Passed: "
        f"{len(passedModels)}"
    )

    for modelKey in (
        passedModels
    ):

        print(
            f"  PASS  {modelKey}"
        )

    print()

    print(
        f"Failed: "
        f"{len(failedModels)}"
    )

    for failure in (
        failedModels
    ):

        print(
            f"  FAIL  "
            f"{failure['model']}"
        )

        print(
            f"        "
            f"{failure['error']}"
        )

    if failedModels:

        raise RuntimeError(
            f"{len(failedModels)} "
            "pipeline test(s) failed."
        )


if __name__ == "__main__":

    main()