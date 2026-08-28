from app.models.state import ScanState

from app.agents.discovery.config import (
    DiscoveryConfig,
    defaultDiscoveryConfig,
)

from app.agents.discovery.search import (
    gatherDiscoveryEvidence,
)

from app.agents.discovery.coverage import (
    improveDiscoveryCoverage,
)

from app.agents.discovery.evidenceMatcher import (
    groupModelEvidence,
)

from app.database.db import (
    saveDiscoveryCandidate,
    updateScanStage,
)


def discoveryAgent(
    state: ScanState,
) -> dict:

    objective = state["query"]

    scanId = state.get("scanId")

    if scanId is not None:
        updateScanStage(
            scanId,
            "discovery",
        )

    # =================================================
    # CONFIG
    # =================================================

    discoveryConfigData = state.get("discoveryConfig")

    if discoveryConfigData:
        discoveryConfig = DiscoveryConfig(**discoveryConfigData)
    else:
        discoveryConfig = defaultDiscoveryConfig

    # =================================================
    # GATHER EVIDENCE
    # =================================================

    discoveryEvidence = gatherDiscoveryEvidence(
        objective,
        discoveryConfig,
    )

    if discoveryConfig.enableCoverageImprovement:
        discoveryEvidence = improveDiscoveryCoverage(
            objective,
            discoveryEvidence,
            discoveryConfig,
        )

    # =================================================
    # CREATE CANDIDATES
    # =================================================

    candidates = groupModelEvidence(
        discoveryEvidence,
        discoveryConfig,
    )

    candidates = candidates[: discoveryConfig.maxCandidates]

    # =================================================
    # SAVE CANDIDATES
    # =================================================

    if scanId is not None:

        for candidatePackage in candidates:

            candidateId = saveDiscoveryCandidate(
                scanId,
                candidatePackage,
            )

            candidatePackage["candidateId"] = candidateId

    return {
        "candidates": candidates,
    }
