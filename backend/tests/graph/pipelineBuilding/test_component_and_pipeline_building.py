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


MODEL_NAME = "Whisper Small"
MODEL_SOURCE = "openai/whisper-small"

MODEL_ID = "89ad20fe7b044a7e90774afae8f44ba9"

# Windows / WSL
# DATASET_ID = "b68dd036d6514d68822f717fd52c99ee"

# Mac
DATASET_ID = "30ab6615fd76498ab8642e104575d205"


def main():

    # ----------------------------------------
    # 1. Component building
    # ----------------------------------------

    componentResult = (
        runComponentBuildingWorkflow(
            modelName=MODEL_NAME,
            source=MODEL_SOURCE,
            forceBuild=False,
        )
    )

    print()
    print("=" * 60)
    print("COMPONENT BUILDING RESULT")
    print("=" * 60)

    pprint(
        componentResult,
        sort_dicts=False,
    )

    if (
        componentResult.get("status")
        != "completed"
    ):
        raise RuntimeError(
            "Component building failed. "
            f"Status: "
            f"{componentResult.get('status')}"
        )

    # ----------------------------------------
    # 2. Pipeline building
    # ----------------------------------------

    pipelineResult = (
        runPipelineBuildingWorkflow(
            modelName=MODEL_NAME,
            modelId=MODEL_ID,
            datasetId=DATASET_ID,
            componentResult=componentResult,
        )
    )

    print()
    print("=" * 60)
    print("PIPELINE BUILDING RESULT")
    print("=" * 60)

    pprint(
        pipelineResult,
        sort_dicts=False,
    )

    if (
        pipelineResult.get("status")
        != "completed"
    ):
        raise RuntimeError(
            "Pipeline building failed. "
            f"Status: "
            f"{pipelineResult.get('status')}"
        )

    # ----------------------------------------
    # 3. Pipeline running
    # ----------------------------------------

    runResult = runPipeline(
        pipelineResult[
            "pipelinePath"
        ]
    )

    print()
    print("=" * 60)
    print("PIPELINE RUN RESULT")
    print("=" * 60)

    pprint(
        runResult,
        sort_dicts=False,
    )


if __name__ == "__main__":
    main()