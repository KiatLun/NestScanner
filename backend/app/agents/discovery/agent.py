from app.models.state import ScanState

from app.agents.discovery.config import (
    DiscoveryConfig,
    defaultDiscoveryConfig,
)

from app.agents.discovery.search import (
    gatherDiscoveryEvidence,
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

    candidates = []

    for evidence in discoveryEvidence:

        if evidence.get("source") != "huggingface":
            continue

        metadata = evidence.get(
            "metadata",
            {},
        )
        repositoryId = metadata.get(
            "repositoryId"
        )

        if not repositoryId:
            continue

        candidate = {
            "name": repositoryId.split("/")[-1],

            "organisation": metadata.get(
                "organisation"
            ),

            "repositoryId": repositoryId,

            "sourceUrl": evidence.get(
                "url"
            ),

            "pipelineTag": metadata.get(
                "pipelineTag"
            ),

            "downloads": metadata.get(
                "downloads"
            ),

            "likes": metadata.get(
                "likes"
            ),

            "trendingScore": metadata.get(
                "trendingScore"
            ),

            "createdAt": metadata.get(
                "createdAt"
            ),

            "lastModified": metadata.get(
                "lastModified"
            ),

            "revision": metadata.get(
                "revision"
            ),

            "tags": metadata.get(
                "tags",
                []
            ),
        }

        candidates.append(
            {
                "candidate": candidate,
                "discoveryEvidence": [
                    evidence
                ],
            }
        )
    

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
