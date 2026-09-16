from app.models.state import ScanState

from app.agents.discovery.config import (
    DiscoveryConfig,
    defaultDiscoveryConfig,
)

from app.agents.discovery.search import (
    gatherDiscoveryEvidence,
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

    print("\n=== CANDIDATES BEFORE DATABASE SAVE ===")

    for candidatePackage in candidates:
        candidate = candidatePackage["candidate"]

        print(
            candidate.get("name"),
            "|",
            candidate.get("repositoryId"),
        )

    if scanId is not None:

        for candidatePackage in candidates:

            modelId = saveDiscoveryCandidate(
                scanId,
                candidatePackage,
            )

            candidatePackage["modelId"] = modelId

    return {
        "candidates": candidates,
    }
