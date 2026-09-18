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

MODEL_NAME = "Whisper Small"
MODEL_SOURCE = "openai/whisper-small"

# Mac
# DATASET_ID = "30ab6615fd76498ab8642e104575d205"

# Windows / WSL
DATASET_ID = "b68dd036d6514d68822f717fd52c99ee"


researchResult = {
    "candidate": {
        "name": MODEL_NAME,
        "organisation": "OpenAI",
        "sourceUrl": ("https://github.com/openai/whisper"),
        "candidateType": "model",
    },
    "isLocallyDeployable": True,
    "researchEvidence": {
        "deployabilityEvidence": [
            {
                "source": "huggingface",
                "title": MODEL_SOURCE,
                "url": ("https://huggingface.co/" "openai/whisper-small"),
                "description": ("Official Whisper Small " "Hugging Face repository."),
            },
        ],
        "technicalEvidence": [],
    },
}


def main():

    # ----------------------------------------
    # 1. Onboarding
    # ----------------------------------------

    onboardingResult = runOnboardingWorkflow(researchResult)

    print()
    print("=" * 60)
    print("ONBOARDING RESULT")
    print("=" * 60)

    pprint(
        onboardingResult,
        sort_dicts=False,
    )

    if onboardingResult.get("status") != "completed":
        raise RuntimeError(
            "Onboarding did not complete "
            "successfully. "
            f"Status: "
            f"{onboardingResult.get('status')}"
        )

    modelId = onboardingResult.get("clearmlModelId")

    if not modelId:
        raise RuntimeError("Onboarding result does not " "contain clearmlModelId.")

    source = onboardingResult.get("source")

    if not source:
        raise RuntimeError("Onboarding result does not " "contain source.")

    # ----------------------------------------
    # 2. Component building
    # ----------------------------------------

    componentResult = runComponentBuildingWorkflow(
        modelName=MODEL_NAME,
        source=source,
        forceBuild=True,
    )

    print()
    print("=" * 60)
    print("COMPONENT BUILDING RESULT")
    print("=" * 60)

    pprint(
        componentResult,
        sort_dicts=False,
    )

    if componentResult.get("status") != "completed":
        raise RuntimeError(
            "Component building did not "
            "complete successfully. "
            f"Status: "
            f"{componentResult.get('status')}"
        )

    # ----------------------------------------
    # 3. Pipeline building
    # ----------------------------------------

    pipelineResult = runPipelineBuildingWorkflow(
        modelName=MODEL_NAME,
        modelId=modelId,
        datasetId=DATASET_ID,
        componentResult=componentResult,
    )

    print()
    print("=" * 60)
    print("PIPELINE BUILDING RESULT")
    print("=" * 60)

    pprint(
        pipelineResult,
        sort_dicts=False,
    )

    if pipelineResult.get("status") != "completed":
        raise RuntimeError(
            "Pipeline building did not "
            "complete successfully. "
            f"Status: "
            f"{pipelineResult.get('status')}"
        )

    # ----------------------------------------
    # 4. Pipeline execution
    # ----------------------------------------

    runResult = runPipeline(pipelineResult["pipelinePath"])

    print()
    print("=" * 60)
    print("PIPELINE RESULT")
    print("=" * 60)

    pprint(
        runResult,
        sort_dicts=False,
    )


if __name__ == "__main__":
    main()
