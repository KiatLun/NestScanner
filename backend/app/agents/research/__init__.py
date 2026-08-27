from app.models.state import ScanState

from app.agents.research.agent import (
    researchAgent,
)

from app.agents.research.config import (
    defaultResearchConfig,
)

from app.database.db import (
    saveResearchResult,
)


def research_agent(
    state: ScanState,
) -> dict:

    researchConfig = defaultResearchConfig

    scanId = state.get("scanId")

    candidates = state.get(
        "candidates",
        [],
    )

    researchResults = []

    for index, researchInput in enumerate(
        candidates,
        start=1,
    ):

        candidate = researchInput.get(
            "candidate",
            {},
        )

        modelName = candidate.get(
            "name",
            "Unknown",
        )

        candidateId = researchInput.get("candidateId")

        if researchConfig.verbose:
            print(f"\nResearching " f"{index}/{len(candidates)}: " f"{modelName}")

        # =================================================
        # RUN RESEARCH
        # =================================================

        result = researchAgent(
            researchInput,
            researchConfig,
        )

        # =================================================
        # SAVE RESEARCH RESULT
        # =================================================

        if scanId is not None and candidateId is not None:

            researchResultId = saveResearchResult(
                scanId,
                candidateId,
                result,
            )

            result["researchResultId"] = researchResultId

            if researchConfig.verbose:
                print(
                    f"Saved Research result "
                    f"{researchResultId} "
                    f"for candidate "
                    f"{candidateId}"
                )

        researchResults.append(result)

    return {
        "researchResults": researchResults,
    }
