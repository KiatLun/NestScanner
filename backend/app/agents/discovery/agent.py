from datetime import datetime

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
    getModelByRepositoryId,
)


# ============================================================
# TIMESTAMP PARSING
# ============================================================

def parseTimestamp(
    value: str,
) -> datetime:
    """
    Parse an ISO-8601 timestamp.

    Hugging Face may return timestamps ending in Z,
    while the database may store timestamps with an
    explicit timezone offset.
    """

    if value.endswith("Z"):
        value = value[:-1] + "+00:00"

    return datetime.fromisoformat(
        value
    )


# ============================================================
# DETERMINE WHETHER RESEARCH IS NEEDED
# ============================================================

def researchIsNeeded(
    existingModel: dict | None,
    candidate: dict,
) -> bool:
    """
    Determine whether a discovered model should be
    sent to the Research Agent.

    Research is required when:

    1. The model does not exist in the database.
    2. The model exists but has never been researched.
    3. The Hugging Face model was modified after its
       latest completed research.

    Otherwise the existing research is considered
    up to date.
    """

    # =================================================
    # CASE 1:
    # BRAND NEW MODEL
    # =================================================

    if existingModel is None:

        return True

    # =================================================
    # CASE 2:
    # MODEL EXISTS BUT HAS NEVER BEEN RESEARCHED
    # =================================================

    latestResearchCompletedAt = (
        existingModel.get(
            "latestResearchCompletedAt"
        )
    )

    if latestResearchCompletedAt is None:

        return True

    # =================================================
    # CASE 3:
    # NO HF LAST-MODIFIED TIMESTAMP
    # =================================================

    currentLastModified = candidate.get(
        "lastModified"
    )

    if currentLastModified is None:

        return False

    # =================================================
    # CASE 4:
    # MODEL WAS MODIFIED AFTER RESEARCH
    # =================================================

    modelModifiedAt = parseTimestamp(
        currentLastModified
    )

    researchCompletedAt = parseTimestamp(
        latestResearchCompletedAt
    )

    return (
        modelModifiedAt
        > researchCompletedAt
    )


# ============================================================
# DIVERSIFIED CANDIDATE SELECTION
# ============================================================

def selectDiverseHuggingFaceCandidates(
    candidates: list[dict],
    maxCandidates: int,
) -> list[dict]:
    """
    Select research candidates from different Hugging Face
    discovery sources.

    Priority:

    1. Most downloaded
    2. Most liked
    3. Newest
    4. Recently modified

    A model is selected at most once, even if it appears
    in multiple discovery sources.

    This prevents a small maxCandidates value from being
    dominated by newly created models.
    """

    # =================================================
    # SOURCE PRIORITY
    # =================================================

    sourcePriority = [
        "popular",
        "liked",
        "trending",
        "new",
        "recently_modified",
    ]

    selected = []

    selectedRepositoryIds = set()

    # =================================================
    # ROUND 1:
    # SELECT ONE MODEL FROM EACH SOURCE
    # =================================================

    for source in sourcePriority:

        if len(selected) >= maxCandidates:

            break

        for candidatePackage in candidates:

            candidate = candidatePackage.get(
                "candidate",
                {},
            )

            repositoryId = candidate.get(
                "repositoryId"
            )

            if not repositoryId:

                continue

            # -------------------------------------------------
            # Don't select the same repository twice.
            # -------------------------------------------------

            if repositoryId in selectedRepositoryIds:

                continue

            discoverySources = candidate.get(
                "discoverySources",
                [],
            )

            if source not in discoverySources:

                continue

            selected.append(
                candidatePackage
            )

            selectedRepositoryIds.add(
                repositoryId
            )

            print(
                "Selected from "
                f"{source}:",
                repositoryId,
            )

            break

    # =================================================
    # ROUND 2:
    # FILL REMAINING SLOTS
    # =================================================

    if len(selected) < maxCandidates:

        for candidatePackage in candidates:

            if len(selected) >= maxCandidates:

                break

            candidate = candidatePackage.get(
                "candidate",
                {},
            )

            repositoryId = candidate.get(
                "repositoryId"
            )

            if not repositoryId:

                continue

            if repositoryId in selectedRepositoryIds:

                continue

            selected.append(
                candidatePackage
            )

            selectedRepositoryIds.add(
                repositoryId
            )

    return selected


# ============================================================
# DISCOVERY AGENT
# ============================================================

def discoveryAgent(
    state: ScanState,
) -> dict:

    objective = state[
        "query"
    ]

    scanId = state.get(
        "scanId"
    )

    # =================================================
    # UPDATE SCAN STAGE
    # =================================================

    if scanId is not None:

        updateScanStage(
            scanId,
            "discovery",
        )

    # =================================================
    # CONFIG
    # =================================================

    discoveryConfigData = state.get(
        "discoveryConfig"
    )

    if discoveryConfigData:

        discoveryConfig = (
            DiscoveryConfig(
                **discoveryConfigData
            )
        )

    else:

        discoveryConfig = (
            defaultDiscoveryConfig
        )

    # =================================================
    # GATHER DISCOVERY EVIDENCE
    # =================================================

    discoveryEvidence = (
        gatherDiscoveryEvidence(
            objective,
            discoveryConfig,
        )
    )

    # =================================================
    # GET HUGGING FACE RESULTS
    # =================================================

    huggingFaceEvidence = [
        evidence
        for evidence in discoveryEvidence
        if evidence.get(
            "source"
        ) == "huggingface"
    ]

    print(
        "\n=== DISCOVERY RESULTS ==="
    )

    print(
        f"Received {len(huggingFaceEvidence)} "
        "Hugging Face models."
    )

    # =================================================
    # CREATE RESEARCH-ELIGIBLE CANDIDATES
    # =================================================

    candidates = []

    for evidence in huggingFaceEvidence:

        # -------------------------------------------------
        # METADATA
        # -------------------------------------------------

        metadata = evidence.get(
            "metadata",
            {},
        )

        repositoryId = metadata.get(
            "repositoryId"
        )

        # -------------------------------------------------
        # Repository ID is required because it is the
        # unique Hugging Face model identity.
        # -------------------------------------------------

        if not repositoryId:

            continue

        # =================================================
        # BUILD CANDIDATE
        # =================================================

        candidate = {
            "name": (
                repositoryId.split(
                    "/"
                )[-1]
            ),

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
                [],
            ),

            # Important:
            # Preserve which Hugging Face catalogue
            # views discovered this model.
            "discoverySources": metadata.get(
                "discoverySources",
                [],
            ),
        }

        # =================================================
        # CHECK DATABASE
        # =================================================

        existingModel = (
            getModelByRepositoryId(
                repositoryId
            )
        )

        # =================================================
        # CHECK WHETHER RESEARCH IS NEEDED
        # =================================================

        if not researchIsNeeded(
            existingModel,
            candidate,
        ):

            print(
                "Skipping current model:",
                repositoryId,
            )

            continue

        # =================================================
        # LOG WHY MODEL WAS SELECTED FOR RESEARCH
        # =================================================

        if existingModel is None:

            print(
                "NEW MODEL:",
                repositoryId,
            )

        elif existingModel.get(
            "latestResearchCompletedAt"
        ) is None:

            print(
                "UNRESEARCHED MODEL:",
                repositoryId,
            )

        else:

            print(
                "STALE RESEARCH:",
                repositoryId,
            )

        # =================================================
        # ADD TO RESEARCH-ELIGIBLE LIST
        # =================================================

        candidates.append(
            {
                "candidate": candidate,

                "discoveryEvidence": [
                    evidence
                ],
            }
        )

    # =================================================
    # DIVERSIFIED SELECTION
    # =================================================

    candidates = (
        selectDiverseHuggingFaceCandidates(
            candidates,
            discoveryConfig.maxCandidates,
        )
    )

    # =================================================
    # SAVE DISCOVERY CANDIDATES
    # =================================================

    print(
        "\n=== CANDIDATES BEFORE DATABASE SAVE ==="
    )

    print(
        f"Selected {len(candidates)} "
        "models for research."
    )

    for candidatePackage in candidates:

        candidate = candidatePackage[
            "candidate"
        ]

        print(
            candidate.get(
                "name"
            ),
            "|",
            candidate.get(
                "repositoryId"
            ),
            "| downloads:",
            candidate.get(
                "downloads"
            ),
            "| likes:",
            candidate.get(
                "likes"
            ),
            "| sources:",
            ", ".join(
                candidate.get(
                    "discoverySources",
                    [],
                )
            ),
        )

    # =================================================
    # SAVE TO DATABASE
    # =================================================

    if scanId is not None:

        for candidatePackage in candidates:

            modelId = saveDiscoveryCandidate(
                scanId,
                candidatePackage,
            )

            candidatePackage[
                "modelId"
            ] = modelId

    # =================================================
    # RETURN CANDIDATES TO LANGGRAPH
    # =================================================

    return {
        "candidates": candidates,
    }