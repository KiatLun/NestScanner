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
)


def discoveryAgent(
    state: ScanState,
    discoveryConfig: DiscoveryConfig = defaultDiscoveryConfig,
) -> dict:

    objective = state["query"]

    scanId = state.get("scanId")

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

    candidates = groupModelEvidence(
        discoveryEvidence,
        discoveryConfig,
    )

    candidates = candidates[: discoveryConfig.maxCandidates]

    # =================================================
    # SAVE DISCOVERY CANDIDATES
    # =================================================

    if scanId is not None:

        for candidatePackage in candidates:

            candidateId = saveDiscoveryCandidate(
                scanId,
                candidatePackage,
            )

            candidatePackage["candidateId"] = candidateId

            if discoveryConfig.verbose:
                modelName = candidatePackage.get(
                    "candidate",
                    {},
                ).get(
                    "name",
                    "Unknown",
                )

                print(f"Saved Discovery candidate " f"{candidateId}: " f"{modelName}")

    return {
        "candidates": candidates,
    }
