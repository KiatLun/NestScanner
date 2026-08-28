from app.models.state import ScanState

from app.agents.research.agent import (
    researchAgent,
)

from app.agents.research.config import (
    ResearchConfig,
    defaultResearchConfig,
)

from app.database.db import saveResearchResult, updateScanStage


def research_agent(
    state: ScanState,
) -> dict:

    scanId = state.get("scanId")

    if scanId is not None:
        updateScanStage(
            scanId,
            "research",
        )

    candidates = state.get(
        "candidates",
        [],
    )

    # =================================================
    # CONFIG
    # =================================================

    researchConfigData = state.get("researchConfig")

    if researchConfigData:
        researchConfig = ResearchConfig(**researchConfigData)
    else:
        researchConfig = defaultResearchConfig

    # =================================================
    # RESEARCH
    # =================================================

    researchResults = []

    for researchInput in candidates:

        candidateId = researchInput.get("candidateId")

        result = researchAgent(
            researchInput,
            researchConfig,
        )

        if scanId is not None and candidateId is not None:
            researchResultId = saveResearchResult(
                scanId,
                candidateId,
                result,
            )

            result["researchResultId"] = researchResultId

        researchResults.append(result)

    return {
        "researchResults": researchResults,
    }
