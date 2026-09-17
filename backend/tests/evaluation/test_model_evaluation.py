from pprint import pprint

from app.graph.onboarding.workflow import (
    runOnboardingWorkflow,
)

from app.services.echoforge.pipelineBuilder import (
    buildEvaluationPipeline,
    writeEvaluationPipeline,
)

from app.services.echoforge.pipelineRunner import (
    runPipeline,
)

MODEL_NAME = "Whisper Small"
MODEL_SOURCE = "openai/whisper-small"

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
    # 1. Run onboarding
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
            "Onboarding did not complete successfully. "
            f"Status: {onboardingResult.get('status')}"
        )

    # ----------------------------------------
    # 2. Get onboarding outputs
    # ----------------------------------------

    modelId = onboardingResult.get("clearmlModelId")

    if not modelId:
        raise RuntimeError("Onboarding result does not contain " "clearmlModelId.")

    component = onboardingResult.get("inferenceComponent")

    if not component:
        raise RuntimeError("Onboarding result does not contain " "inferenceComponent.")

    print()
    print("=" * 60)
    print("MODEL EVALUATION")
    print("=" * 60)

    print(f"Model name: {MODEL_NAME}")

    print(f"Model ID: {modelId}")

    print(f"Dataset ID: {DATASET_ID}")

    # ----------------------------------------
    # 3. Show resolved inference component
    # ----------------------------------------

    print()
    print("=" * 60)
    print("RESOLVED COMPONENT")
    print("=" * 60)

    pprint(
        component,
        sort_dicts=False,
    )

    imageName = component.get("imageName")

    entryPoint = component.get("entryPoint")

    if not imageName:
        raise RuntimeError(
            "Resolved inference component " "does not contain imageName."
        )

    if not entryPoint:
        raise RuntimeError(
            "Resolved inference component " "does not contain entryPoint."
        )

    print(f"Runtime image: {imageName}")

    print(f"Entry point: {entryPoint}")

    # ----------------------------------------
    # 4. Build evaluation pipeline
    # ----------------------------------------

    pipeline = buildEvaluationPipeline(
        modelName=MODEL_NAME,
        modelId=modelId,
        datasetId=DATASET_ID,
        component=component,
    )

    print()
    print("=" * 60)
    print("PIPELINE")
    print("=" * 60)

    pprint(
        pipeline,
        sort_dicts=False,
    )

    # ----------------------------------------
    # 5. Write pipeline YAML
    # ----------------------------------------

    pipelineResult = writeEvaluationPipeline(
        modelName=MODEL_NAME,
        pipeline=pipeline,
    )

    print()
    print("=" * 60)
    print("PIPELINE FILE")
    print("=" * 60)

    pprint(
        pipelineResult,
        sort_dicts=False,
    )

    # ----------------------------------------
    # 6. Run pipeline
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
