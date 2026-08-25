from models.state import ScanState

from helper.gatherDeeperEvidence import (
    gatherDeeperEvidence,
)

from helper.checkModelLegitimacy import (
    checkModelLegitimacy,
)

from helper.checkLocalDeployability import (
    checkLocalDeployability,
)

from helper.buildTechnicalProfile import (
    buildTechnicalProfile,
)


def researchAgent(
    state: ScanState,
) -> dict:
    """
    Perform deeper investigation on one discovered ASR model.

    Research is responsible for:

    1. Gathering deeper model-specific evidence.
    2. Checking whether the model is legitimate.
    3. Checking whether it can be run locally.
    4. Building a technical model profile.
    """

    print("\n" + "=" * 60)
    print("RESEARCH AGENT")
    print("=" * 60)

    currentModel = state["currentModel"]

    print(f"\nResearching: " f"{currentModel.get('name')}")

    # =================================================
    # 1. GATHER DEEPER EVIDENCE
    # =================================================

    deeperEvidence = gatherDeeperEvidence(currentModel)

    print(f"\nDeeper evidence collected: " f"{len(deeperEvidence)}")

    # =================================================
    # 2. CHECK MODEL LEGITIMACY
    # =================================================

    isLegitimate = checkModelLegitimacy(
        currentModel,
        deeperEvidence,
    )

    print(f"\nLegitimate model: " f"{isLegitimate}")

    # =================================================
    # 3. CHECK LOCAL DEPLOYABILITY
    # =================================================

    isLocallyDeployable = checkLocalDeployability(
        currentModel,
        deeperEvidence,
    )

    print(f"Locally deployable: " f"{isLocallyDeployable}")

    # =================================================
    # 4. BUILD TECHNICAL PROFILE
    # =================================================

    technicalProfile = buildTechnicalProfile(
        currentModel,
        deeperEvidence,
    )

    # =================================================
    # 5. RETURN LANGGRAPH STATE UPDATE
    # =================================================

    return {
        "profile": technicalProfile,
        "researchEvidence": deeperEvidence,
        "isLegitimate": isLegitimate,
        "isLocallyDeployable": (isLocallyDeployable),
    }
