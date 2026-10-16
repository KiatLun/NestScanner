from datetime import datetime

from app.models.state import ScanState

from app.agents.research.agent import (
    researchAgent,
)

from app.agents.research.config import (
    ResearchConfig,
    defaultResearchConfig,
)

from app.database.db import (
    saveResearchResult,
    updateScanStage,
    getModelByRepositoryId,
)


# =====================================================
# HELPERS
# =====================================================

def parseTimestamp(
    timestamp: str | None,
) -> datetime | None:
    """
    Convert an ISO timestamp into a datetime.

    Returns None if the timestamp is missing or invalid.
    """

    if not timestamp:
        return None

    try:
        return datetime.fromisoformat(
            timestamp.replace(
                "Z",
                "+00:00",
            )
        )

    except (ValueError, TypeError):
        return None


def needsResearch(
    candidate: dict,
) -> bool:
    """
    Determine whether a model requires research.

    Research is required when:

    1. No previous research exists.

    OR

    2. The Hugging Face model has been modified after
       the previous research was completed.

    If the model has not changed since the previous
    research, the existing research is reused.
    """

    repositoryId = candidate.get(
        "repositoryId"
    )

    if not repositoryId:
        return True

    # =================================================
    # GET EXISTING MODEL + RESEARCH INFORMATION
    # =================================================

    existingModel = getModelByRepositoryId(
        repositoryId
    )

    if existingModel is None:
        return True

    latestResearchCompletedAt = existingModel.get(
        "latestResearchCompletedAt"
    )

    # No previous completed research exists.
    if not latestResearchCompletedAt:
        return True

    # =================================================
    # GET CURRENT HUGGING FACE MODIFICATION DATE
    # =================================================

    currentLastModified = candidate.get(
        "lastModified"
    )

    # If we do not have a current lastModified value,
    # we cannot prove that the model has changed.
    #
    # Therefore, keep the existing research.
    if not currentLastModified:
        return False

    previousResearchTime = parseTimestamp(
        latestResearchCompletedAt
    )

    currentModifiedTime = parseTimestamp(
        currentLastModified
    )

    # If either timestamp cannot be parsed, rerun
    # research conservatively rather than assuming
    # the existing result is still valid.
    if (
        previousResearchTime is None
        or currentModifiedTime is None
    ):
        return True

    # =================================================
    # COMPARE DATES
    # =================================================

    if currentModifiedTime > previousResearchTime:
        return True

    return False


# =====================================================
# LANGGRAPH RESEARCH NODE
# =====================================================

def research_agent(
    state: ScanState,
) -> dict:
    """
    Research all candidates produced by the Discovery Agent.

    For each model:

    1. Check whether previous research exists.
    2. Check whether the Hugging Face model was modified
       after the previous research.
    3. Run the Research Agent only when necessary.
    4. Save new research results against the current scan.

    Existing research is not deleted or overwritten because
    research_results are associated with individual scans.
    This preserves historical research results.
    """

    scanId = state.get(
        "scanId"
    )

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

    researchConfigData = state.get(
        "researchConfig"
    )

    if researchConfigData:
        researchConfig = ResearchConfig(
            **researchConfigData
        )
    else:
        researchConfig = defaultResearchConfig

    # =================================================
    # RESEARCH
    # =================================================

    researchResults = []

    for researchInput in candidates:

        modelId = researchInput.get(
            "modelId"
        )

        candidate = researchInput.get(
            "candidate",
            {},
        )

        if modelId is None:
            print(
                "Skipping candidate without modelId:",
                candidate.get("name"),
            )
            continue

        repositoryId = candidate.get(
            "repositoryId"
        )

        print(
            "\n================================================="
        )

        print(
            "Checking research:",
            candidate.get("name"),
        )

        print(
            "Repository:",
            repositoryId,
        )

        print(
            "Current lastModified:",
            candidate.get("lastModified"),
        )

        # =================================================
        # CHECK WHETHER RESEARCH IS NEEDED
        # =================================================

        if not needsResearch(
            candidate
        ):

            print(
                "Research is up to date. Skipping:",
                candidate.get("name"),
            )

            continue

        # =================================================
        # RUN RESEARCH
        # =================================================

        print(
            "Research required:",
            candidate.get("name"),
        )

        print(
            "Running Research Agent..."
        )

        result = researchAgent(
            researchInput,
            researchConfig,
        )

        # =================================================
        # SAVE RESEARCH RESULT
        # =================================================

        if scanId is not None:

            researchResultId = saveResearchResult(
                scanId,
                modelId,
                result,
            )

            result["researchResultId"] = (
                researchResultId
            )

            print(
                "Saved research result:",
                researchResultId,
            )

        researchResults.append(
            result
        )

    print(
        "\n================================================="
    )

    print(
        "Research stage completed."
    )

    print(
        "New research results:",
        len(researchResults),
    )

    return {
        "researchResults": researchResults,
    }