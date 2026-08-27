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


def discoveryAgent(
    state: ScanState,
    config: DiscoveryConfig = defaultDiscoveryConfig,
) -> dict:

    objective = state["query"]

    discoveryEvidence = gatherDiscoveryEvidence(
        objective,
        config,
    )

    if config.enableCoverageImprovement:
        discoveryEvidence = improveDiscoveryCoverage(
            objective,
            discoveryEvidence,
            config,
        )

    candidates = groupModelEvidence(
        discoveryEvidence,
        config,
    )

    return {
        "candidates": candidates[: config.maxCandidates],
    }
