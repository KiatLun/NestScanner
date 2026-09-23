from pprint import pprint

from app.graph.onboarding.workflow import (
    runOnboardingWorkflow,
)

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
    # "mega-asr",
    # "fun-asr-nano-2512",
    # "sensevoice-small",
    # "paraformer-en",
    # "voxtral-mini-3b-2507",
    # "whisper-medium",
    # "whisper-small",
    # "wav2vec2-base-960h",
    "hubert-large-ls960-ft",
    # "voxtral-mini-4b-realtime-2602",
    # "silero-vad",
    # "deepspeech-0.9.3",
    # "example-direct-asr",
]


# ============================================================
# Model test configuration
# ============================================================

modelTestConfig = {
    "wav2vec2-base-960h": {
        "modelFamily": "wav2vec2",
        "expectGenerated": True,
    },
    "hubert-large-ls960-ft": {
        "modelFamily": "hubert",
        "expectGenerated": True,
    },
    "qwen3-asr-1.7b": {
        "modelFamily": "qwen",
        "expectGenerated": False,
    },
    "mega-asr": {
        "modelFamily": "mega-asr",
        "expectGenerated": True,
    },
    "fun-asr-nano-2512": {
        "modelFamily": "fun-asr",
        "expectGenerated": True,
    },
    "sensevoice-small": {
        "modelFamily": "sensevoice",
        "expectGenerated": True,
    },
    "paraformer-en": {
        "modelFamily": "paraformer",
        "expectGenerated": True,
    },
    "voxtral-mini-3b-2507": {
        "modelFamily": "voxtral",
        "expectGenerated": False,
    },
    "whisper-medium": {
        "modelFamily": "whisper",
        "expectGenerated": False,
    },
    "whisper-small": {
        "modelFamily": "whisper",
        "expectGenerated": False,
    },
    "voxtral-mini-4b-realtime-2602": {
        "modelFamily": "voxtral",
        "expectGenerated": False,
    },
    "silero-vad": {
        "modelFamily": "silero",
        "expectGenerated": False,
    },
    "deepspeech-0.9.3": {
        "modelFamily": "deepspeech",
        "expectGenerated": True,
    },
    "example-direct-asr": {
        "modelFamily": "example-direct-asr",
        "expectGenerated": True,
    },
}


# ============================================================
# Dataset
# ============================================================

# Mac
# DATASET_ID = "30ab6615fd76498ab8642e104575d205"

# Windows / WSL
DATASET_ID = "b68dd036d6514d68822f717fd52c99ee"


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

    printSection(f"END-TO-END TEST: {modelKey}")

    # --------------------------------------------------------
    # Validate fixtures
    # --------------------------------------------------------

    if modelKey not in researchAgentOutput:

        raise RuntimeError("Research fixture not found: " f"{modelKey}")

    if modelKey not in modelTestConfig:

        raise RuntimeError("Model test config not found: " f"{modelKey}")

    # --------------------------------------------------------
    # Load test configuration
    # --------------------------------------------------------

    researchResult = researchAgentOutput[modelKey]

    testConfig = modelTestConfig[modelKey]

    candidate = researchResult["candidate"]

    modelName = candidate["name"]

    modelFamily = testConfig["modelFamily"]

    expectGenerated = testConfig["expectGenerated"]

    print(f"Model key: {modelKey}")

    print(f"Model: {modelName}")

    print(f"Family: {modelFamily}")

    print("Expected component: " f"{'generated' if expectGenerated else 'existing'}")

    print(f"Dataset ID: {DATASET_ID}")

    # ========================================================
    # 1. Onboarding
    # ========================================================

    printSection("ONBOARDING")

    onboardingResult = runOnboardingWorkflow(researchResult)

    printSection("ONBOARDING RESULT")

    pprint(
        onboardingResult,
        sort_dicts=False,
    )

    if onboardingResult.get("status") != "completed":

        raise RuntimeError(
            "Onboarding did not complete "
            "successfully.\n"
            f"Status: "
            f"{onboardingResult.get('status')}\n"
            f"Error: "
            f"{onboardingResult.get('error')}"
        )

    modelId = onboardingResult.get("clearmlModelId")

    if not modelId:

        raise RuntimeError("Onboarding result does not " "contain clearmlModelId.")

    source = onboardingResult.get("source")

    if not source:

        source = candidate.get("sourceUrl")

    if not source:

        raise RuntimeError(
            "No model source found from " "onboarding or research result."
        )

    print()
    print(f"ClearML Model ID: {modelId}")

    print(f"Source: {source}")

    # ========================================================
    # 2. Component Building
    # ========================================================

    technicalProfile = {
        "candidate": candidate,
        "isLocallyDeployable": (researchResult["isLocallyDeployable"]),
        "researchEvidence": (researchResult["researchEvidence"]),
    }

    printSection("COMPONENT BUILDING")

    componentResult = runComponentBuildingWorkflow(
        modelName=modelName,
        source=source,
        modelFamily=modelFamily,
        technicalProfile=(technicalProfile),
        forceBuild=True,
    )

    printSection("COMPONENT BUILDING RESULT")

    pprint(
        componentResult,
        sort_dicts=False,
    )

    if componentResult.get("status") != "completed":

        raise RuntimeError(
            "Component building did not "
            "complete successfully.\n"
            f"Status: "
            f"{componentResult.get('status')}\n"
            f"Error: "
            f"{componentResult.get('error')}"
        )

    # --------------------------------------------------------
    # Validate expected component route
    # --------------------------------------------------------

    inferenceComponent = componentResult.get("inferenceComponent")

    if not inferenceComponent:

        raise RuntimeError(
            "Component Building did not return " "an inferenceComponent."
        )

    matchedBy = inferenceComponent.get("matchedBy")

    if expectGenerated:

        if matchedBy != "generated":

            raise RuntimeError(
                "Expected Component Creation Agent "
                "to generate a component, but "
                f"matchedBy={matchedBy}"
            )

    else:

        if matchedBy == "generated":

            raise RuntimeError(
                "Expected an existing component, "
                "but Component Creation Agent "
                "generated a new one."
            )

    # ========================================================
    # 3. Pipeline Building
    # ========================================================

    printSection("PIPELINE BUILDING")

    pipelineResult = runPipelineBuildingWorkflow(
        modelName=modelName,
        modelId=modelId,
        datasetId=DATASET_ID,
        componentResult=(componentResult),
    )

    printSection("PIPELINE BUILDING RESULT")

    pprint(
        pipelineResult,
        sort_dicts=False,
    )

    if pipelineResult.get("status") != "completed":

        raise RuntimeError(
            "Pipeline building did not "
            "complete successfully.\n"
            f"Status: "
            f"{pipelineResult.get('status')}\n"
            f"Error: "
            f"{pipelineResult.get('error')}"
        )

    pipelinePath = pipelineResult.get("pipelinePath")

    if not pipelinePath:

        raise RuntimeError(
            "Pipeline Building completed but " "pipelinePath was not returned."
        )

    # ========================================================
    # 4. Pipeline Execution
    # ========================================================

    printSection("PIPELINE EXECUTION")

    runResult = runPipeline(pipelinePath)

    printSection("PIPELINE RESULT")

    pprint(
        runResult,
        sort_dicts=False,
    )

    if runResult.get("status") != "submitted":

        raise RuntimeError(
            "Pipeline execution was not "
            "submitted successfully.\n"
            f"Status: "
            f"{runResult.get('status')}\n"
            f"Error: "
            f"{runResult.get('error')}"
        )

    # ========================================================
    # Success
    # ========================================================

    printSection(f"TEST PASSED: {modelKey}")

    return {
        "modelKey": modelKey,
        "modelName": modelName,
        "modelId": modelId,
        "onboardingResult": (onboardingResult),
        "componentResult": (componentResult),
        "pipelineResult": (pipelineResult),
        "runResult": (runResult),
    }


# ============================================================
# Main
# ============================================================


def main():

    printSection("FULL END-TO-END TEST")

    passedModels = []
    failedModels = []

    for modelKey in modelsToTest:

        try:

            runModelTest(modelKey)

            passedModels.append(modelKey)

        except Exception as error:

            failedModels.append(
                {
                    "model": modelKey,
                    "error": str(error),
                }
            )

            printSection(f"TEST FAILED: {modelKey}")

            print(str(error))

    # ========================================================
    # Summary
    # ========================================================

    printSection("TEST SUMMARY")

    print(f"Passed: {len(passedModels)}")

    for modelKey in passedModels:

        print(f"  PASS  {modelKey}")

    print()

    print(f"Failed: {len(failedModels)}")

    for failure in failedModels:

        print(f"  FAIL  " f"{failure['model']}")

        print(f"        " f"{failure['error']}")

    if failedModels:

        raise RuntimeError(f"{len(failedModels)} " "end-to-end test(s) failed.")


if __name__ == "__main__":

    main()
