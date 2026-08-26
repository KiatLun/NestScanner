from app.agents.research.releaseDate import (
    determineReleaseDate,
)

from app.agents.research.checkRecency import (
    checkRecency,
)

from app.agents.research.gatherEvidence import (
    gatherResearchEvidence,
)

from app.agents.research.checkDeployability import (
    checkDeployability,
)

from app.agents.research.technicalProfile import (
    buildTechnicalProfile,
)


def researchAgent(
    researchInput: dict,
) -> dict:
    """
    Research one candidate produced by Discovery.

    Research checks:
    1. Recency
    2. Local deployability

    Only candidates that pass both checks proceed
    to technical profiling.
    """

    candidate = researchInput[
        "candidate"
    ]

    discoveryEvidence = researchInput.get(
        "discoveryEvidence",
        [],
    )

    # =================================================
    # 1. GATHER RESEARCH EVIDENCE
    # =================================================

    researchEvidence = gatherResearchEvidence(
        candidate,
        discoveryEvidence,
    )

    # =================================================
    # 2. DETERMINE RELEASE DATE
    # =================================================

    releaseDate = determineReleaseDate(
        candidate,
        researchEvidence,
    )

    # =================================================
    # 3. CHECK RECENCY
    # =================================================

    isRecent = checkRecency(
        releaseDate,
        days=30,
    )

    if not isRecent:
        return {
            "candidate": candidate,
            "releaseDate": releaseDate,
            "isRecent": False,
            "isLocallyDeployable": None,
            "profile": None,
            "researchEvidence": researchEvidence,
        }

    # =================================================
    # 4. CHECK LOCAL DEPLOYABILITY
    # =================================================

    isLocallyDeployable = checkDeployability(
        candidate,
        researchEvidence,
    )

    if not isLocallyDeployable:
        return {
            "candidate": candidate,
            "releaseDate": releaseDate,
            "isRecent": True,
            "isLocallyDeployable": False,
            "profile": None,
            "researchEvidence": researchEvidence,
        }

    # =================================================
    # 5. BUILD TECHNICAL PROFILE
    # =================================================

    profile = buildTechnicalProfile(
        candidate,
        researchEvidence,
        releaseDate,
    )

    return {
        "candidate": candidate,
        "releaseDate": releaseDate,
        "isRecent": True,
        "isLocallyDeployable": True,
        "profile": profile,
        "researchEvidence": researchEvidence,
    }