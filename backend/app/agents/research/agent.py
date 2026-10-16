from app.agents.research.config import (
    ResearchConfig,
    defaultResearchConfig,
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
    """
    Research one model discovered by the Discovery Agent.

    The Research Agent is responsible for:

    1. Evaluating whether the model can be deployed locally.
    2. Building a technical profile for the exact model.
    3. Gathering evidence supporting both findings.

    Recency is NOT handled here.

    Model freshness is handled by the Discovery pipeline
    using Hugging Face metadata such as lastModified.
    """

    # =================================================
    # 1. VALIDATE INPUT
    # =================================================

    if not isinstance(
        researchInput,
        dict,
    ):
        raise TypeError(
            "researchInput must be a dictionary."
        )

    candidate = researchInput.get(
        "candidate"
    )

    if not isinstance(
        candidate,
        dict,
    ):
        raise ValueError(
            "researchInput must contain a "
            "'candidate' dictionary."
        )

    discoveryEvidence = researchInput.get(
        "discoveryEvidence",
        [],
    )

    if not isinstance(
        discoveryEvidence,
        list,
    ):
        discoveryEvidence = []


    # =================================================
    # 2. LOCAL DEPLOYABILITY
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

    if not isinstance(
        deployabilityEvidence,
        list,
    ):
        deployabilityEvidence = []


    # =================================================
    # 3. TECHNICAL PROFILE
    # =================================================

    # Technical research is performed regardless of
    # local deployability.
    #
    # A model that cannot currently be deployed locally
    # can still have useful information such as:
    #
    # - architecture
    # - parameter count
    # - languages
    # - license
    # - base model
    # - model lineage
    # - WER
    # - benchmark information
    # - training datasets
    # - fine-tuning support
    # - inference framework
    #
    # buildTechnicalProfile performs:
    #
    # HF metadata/model-card research
    #       ↓
    # information-gap analysis
    #       ↓
    # targeted external research
    #       ↓
    # final LLM extraction

    profileResult = buildTechnicalProfile(
        candidate,
        discoveryEvidence,
        deployabilityEvidence,
        candidate.get("createdAt"),
        researchConfig,
    )

    technicalProfile = profileResult.get(
        "technicalProfile"
    )

    technicalEvidence = profileResult.get(
        "evidence",
        [],
    )

    if not isinstance(
        technicalEvidence,
        list,
    ):
        technicalEvidence = []


    # =================================================
    # 4. RELEASE DATE
    # =================================================

    # Discovery already provides createdAt from
    # Hugging Face.
    #
    # Until a separate authoritative release-date
    # mechanism is introduced, use createdAt.

    releaseDate = profileResult.get(
        "releaseDate",
        candidate.get("createdAt"),
    )


    # =================================================
    # 5. RETURN RESEARCH RESULT
    # =================================================

    return {
        "releaseDate": releaseDate,

        "isLocallyDeployable": (
            isLocallyDeployable
        ),

        "technicalProfile": (
            technicalProfile
        ),

        "researchEvidence": {
            "deployabilityEvidence": (
                deployabilityEvidence
            ),

            "technicalEvidence": (
                technicalEvidence
            ),
        },
    }