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

    recencyEvidence = recencyResult.get(
        "evidence",
        [],
    )

    if not recencyResult.get(
        "isRecent",
        False,
    ):
        return {
            "releaseDate": releaseDate,
            "isRecent": False,
            "isLocallyDeployable": None,
            "technicalProfile": None,
            "researchEvidence": {
                "recencyEvidence": (recencyEvidence),
                "deployabilityEvidence": [],
                "technicalEvidence": [],
            },
        }

    # =================================================
    # 2. DEPLOYABILITY
    # =================================================

    deployabilityResult = checkDeployability(
        candidate,
        discoveryEvidence,
        researchConfig,
    )

    deployabilityEvidence = deployabilityResult.get(
        "evidence",
        [],
    )

    if not deployabilityResult.get(
        "isLocallyDeployable",
        False,
    ):
        return {
            "releaseDate": releaseDate,
            "isRecent": True,
            "isLocallyDeployable": False,
            "technicalProfile": None,
            "researchEvidence": {
                "recencyEvidence": (recencyEvidence),
                "deployabilityEvidence": (deployabilityEvidence),
                "technicalEvidence": [],
            },
        }

    # =================================================
    # 3. TECHNICAL PROFILE
    # =================================================

    profileResult = buildTechnicalProfile(
        candidate,
        discoveryEvidence,
        recencyEvidence,
        deployabilityEvidence,
        releaseDate,
        researchConfig,
    )

    return {
        "releaseDate": releaseDate,
        "isRecent": True,
        "isLocallyDeployable": True,
        "technicalProfile": (profileResult.get("technicalProfile")),
        "researchEvidence": {
            "recencyEvidence": (recencyEvidence),
            "deployabilityEvidence": (deployabilityEvidence),
            "technicalEvidence": (
                profileResult.get(
                    "evidence",
                    [],
                )
            ),
        },
    }
