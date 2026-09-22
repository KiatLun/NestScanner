from pathlib import Path
from pprint import pprint

from app.graph.pipelineBuilding.workflow import (
    runPipelineBuildingWorkflow,
)

from app.services.echoforge.pipelineRunner import (
    runPipeline,
)

# ============================================================
# TEST INPUT
# ============================================================

MODEL_NAME = "sensevoice-small"

# ClearML Model ID returned by onboarding
CLEARML_MODEL_ID = "a8ae573645524df8b4f39f664bce75ef"

# Current ClearML dataset

# Windows / WSL
# DATASET_ID = "b68dd036d6514d68822f717fd52c99ee"

# Mac
DATASET_ID = "30ab6615fd76498ab8642e104575d205"


# ============================================================
# COMPONENT BUILDING RESULT
# ============================================================

componentResult = {
    "modelName": MODEL_NAME,
    "status": "completed",
    "inferenceComponent": {
        "component": "stt_inference_sensevoice",
        "family": "sensevoice",
        "componentDir": (
            "/Users/aaronjt/Documents/echoforge/components/"
            "inference_component/stt_inference/"
            "stt_inference_sensevoice"
        ),
        "mainFile": (
            "/Users/aaronjt/Documents/echoforge/components/"
            "inference_component/stt_inference/"
            "stt_inference_sensevoice/main.py"
        ),
        "dockerfile": (
            "/Users/aaronjt/Documents/echoforge/components/"
            "inference_component/stt_inference/"
            "stt_inference_sensevoice/Dockerfile"
        ),
        "requirementsFile": (
            "/Users/aaronjt/Documents/echoforge/components/"
            "inference_component/stt_inference/"
            "stt_inference_sensevoice/requirements.txt"
        ),
        "imageName": "stt_inference_sensevoice:latest",
        "entryPoint": "/app/main.py",
        "matchedBy": "generated",
    },
    "evaluationComponent": {
        "component": "stt_evaluation",
        "imageName": "stt_evaluation:latest",
        "entryPoint": "/app/main.py",
    },
}

def main():

    print()
    print("=" * 70)
    print("PIPELINE BUILDING + RUNNER TEST")
    print("=" * 70)

    print(f"Model: {MODEL_NAME}")
    print(f"ClearML Model ID: {CLEARML_MODEL_ID}")
    print(f"Dataset ID: {DATASET_ID}")

    # --------------------------------------------------------
    # 1. Run Pipeline Building
    # --------------------------------------------------------

    pipelineResult = runPipelineBuildingWorkflow(
        modelName=MODEL_NAME,
        modelId=CLEARML_MODEL_ID,
        datasetId=DATASET_ID,
        componentResult=componentResult,
    )

    # --------------------------------------------------------
    # 2. Print Pipeline Building result
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("PIPELINE BUILDING RESULT")
    print("=" * 70)

    pprint(
        pipelineResult,
        sort_dicts=False,
    )

    # --------------------------------------------------------
    # 3. Validate Pipeline Building status
    # --------------------------------------------------------

    if pipelineResult.get("status") != "completed":

        raise RuntimeError(
            "Pipeline Building failed.\n"
            f"Status: {pipelineResult.get('status')}\n"
            f"Error: {pipelineResult.get('error')}"
        )

    # --------------------------------------------------------
    # 4. Validate generated pipeline YAML
    # --------------------------------------------------------

    pipelinePath = (
        pipelineResult.get("pipelinePath")
        or pipelineResult.get("pipelineFile")
        or pipelineResult.get("pipelineYaml")
    )

    if not pipelinePath:

        raise RuntimeError(
            "Pipeline Building completed but " "no pipeline path was returned."
        )

    pipelinePath = Path(pipelinePath)

    print()
    print("=" * 70)
    print("PIPELINE YAML")
    print("=" * 70)

    print(pipelinePath)

    if not pipelinePath.exists():

        raise RuntimeError("Generated pipeline YAML " f"does not exist: {pipelinePath}")

    # --------------------------------------------------------
    # 5. Check generated entry point
    # --------------------------------------------------------

    pipelineContent = pipelinePath.read_text(encoding="utf-8")

    expectedEntryPoint = "/app/main.py"

    if expectedEntryPoint not in pipelineContent:

        raise RuntimeError(
            "Generated pipeline YAML does not "
            "contain the expected inference "
            "entry point:\n"
            f"{expectedEntryPoint}"
        )

    print()
    print("[Test] Inference entry point: " f"{expectedEntryPoint}")

    # --------------------------------------------------------
    # 6. Run Pipeline
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("RUNNING PIPELINE")
    print("=" * 70)

    runResult = runPipeline(str(pipelinePath))

    # --------------------------------------------------------
    # 7. Print Pipeline Runner result
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("PIPELINE RUNNER RESULT")
    print("=" * 70)

    pprint(
        runResult,
        sort_dicts=False,
    )

    # --------------------------------------------------------
    # 8. Validate Pipeline Runner
    # --------------------------------------------------------

    if runResult.get("status") != "submitted":

        raise RuntimeError(
            "Pipeline Runner failed.\n"
            f"Status: {runResult.get('status')}\n"
            f"Error: {runResult.get('error')}"
        )

    # --------------------------------------------------------
    # Success
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("TEST PASSED")
    print("=" * 70)

    print("Pipeline successfully:")

    print("1. Built the inference stage")
    print("2. Built the evaluation stage")
    print("3. Linked the stages")
    print("4. Generated the pipeline YAML")
    print("5. Verified /app/main.py entry point")
    print("6. Submitted the pipeline to ClearML")


if __name__ == "__main__":
    main()
