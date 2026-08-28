from app.agents.research.config import (
    ResearchConfig,
    defaultResearchConfig,
)

from app.agents.research.checkRecency import (
    checkRecency,
)

from app.agents.research.checkDeployability import (
    checkDeployability,
)

from app.agents.research.buildTechnicalProfile import (
    buildTechnicalProfile,
)


def researchAgent(
    researchInput: dict,
    researchConfig: ResearchConfig = defaultResearchConfig,
) -> dict:

    candidate = researchInput["candidate"]

    discoveryEvidence = researchInput.get(
        "discoveryEvidence",
        [],
    )

    # =================================================
    # 1. RECENCY
    # =================================================

    recencyResult = checkRecency(
        candidate,
        discoveryEvidence,
        researchConfig,
    )

    releaseDate = recencyResult.get("releaseDate")

    isRecent = recencyResult.get(
        "isRecent",
        False,
    )

    recencyEvidence = recencyResult.get(
        "evidence",
        [],
    )

    # =================================================
    # 2. DEPLOYABILITY
    # =================================================

    deployabilityResult = checkDeployability(
        candidate,
        discoveryEvidence,
        researchConfig,
    )

    isLocallyDeployable = deployabilityResult.get(
        "isLocallyDeployable",
        False,
    )

    deployabilityEvidence = deployabilityResult.get(
        "evidence",
        [],
    )

    # =================================================
    # 3. TECHNICAL PROFILE
    # =================================================

    technicalProfile = None
    technicalEvidence = []

    if isRecent and isLocallyDeployable:

        profileResult = buildTechnicalProfile(
            candidate,
            discoveryEvidence,
            recencyEvidence,
            deployabilityEvidence,
            releaseDate,
            researchConfig,
        )

        technicalProfile = profileResult.get("technicalProfile")

        technicalEvidence = profileResult.get(
            "evidence",
            [],
        )

    # =================================================
    # 4. RETURN RESULT
    # =================================================

    return {
        "releaseDate": releaseDate,
        "isRecent": isRecent,
        "isLocallyDeployable": (isLocallyDeployable),
        "technicalProfile": (technicalProfile),
        "researchEvidence": {
            "recencyEvidence": (recencyEvidence),
            "deployabilityEvidence": (deployabilityEvidence),
            "technicalEvidence": (technicalEvidence),
        },
    }
