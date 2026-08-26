from app.models.state import ScanState

from app.agents.discovery.search import (
    gatherDiscoveryEvidence,
)

from app.agents.discovery.coverage import (
    improveDiscoveryCoverage,
)

from app.agents.discovery.evidenceMatcher import (
    groupModelEvidence,
)

def discoveryAgent(
    state: ScanState,
) -> dict:

    objective = state["query"]

    discoveryEvidence = gatherDiscoveryEvidence(
        objective
    )

    discoveryEvidence = improveDiscoveryCoverage(
        objective,
        discoveryEvidence,
    )

    candidates = groupModelEvidence(
        discoveryEvidence
    )

    return {
        "candidates": candidates,
    }