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
) -> dict:
    """
    Research one candidate produced by Discovery.

    Research performs:
    1. Recency check
    2. Local deployability check
    3. Technical profiling

    Technical profiling only happens when both
    checks pass.
    """

    candidate = researchInput[
        "candidate"
    ]

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
        60
    )

    if not recencyResult.get(
        "isRecent",
        False,
    ):
        return {
            "candidate": candidate,
            "releaseDate": recencyResult.get(
                "releaseDate"
            ),
            "isRecent": False,
            "isLocallyDeployable": None,
            "profile": None,
            "researchEvidence": {
                "recencyEvidence": recencyResult.get(
                    "evidence",
                    [],
                ),
            },
        }

    # =================================================
    # 2. LOCAL DEPLOYABILITY
    # =================================================

    deployabilityResult = checkDeployability(
        candidate,
        discoveryEvidence,
    )

    if not deployabilityResult.get(
        "isLocallyDeployable",
        False,
    ):
        return {
            "candidate": candidate,
            "releaseDate": recencyResult.get(
                "releaseDate"
            ),
            "isRecent": True,
            "isLocallyDeployable": False,
            "profile": None,
            "researchEvidence": {
                "recencyEvidence": recencyResult.get(
                    "evidence",
                    [],
                ),
                "deployabilityEvidence": (
                    deployabilityResult.get(
                        "evidence",
                        [],
                    )
                ),
            },
        }

    # =================================================
    # 3. TECHNICAL PROFILE
    # =================================================

    profileResult = buildTechnicalProfile(
        candidate,
        discoveryEvidence,
        recencyResult.get(
            "evidence",
            [],
        ),
        deployabilityResult.get(
            "evidence",
            [],
        ),
        recencyResult.get(
            "releaseDate"
        ),
    )

    return {
        "candidate": candidate,
        "releaseDate": recencyResult.get(
            "releaseDate"
        ),
        "isRecent": True,
        "isLocallyDeployable": True,
        "profile": profileResult.get(
            "profile"
        ),
        "researchEvidence": {
            "recencyEvidence": recencyResult.get(
                "evidence",
                [],
            ),
            "deployabilityEvidence": (
                deployabilityResult.get(
                    "evidence",
                    [],
                )
            ),
            "technicalEvidence": profileResult.get(
                "evidence",
                [],
            ),
        },
    }