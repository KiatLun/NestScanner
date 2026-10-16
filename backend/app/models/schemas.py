from typing import Any, Literal

from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    source: str
    title: str
    url: str

    description: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class Candidate(BaseModel):
    name: str
    organisation: str | None = None
    sourceUrl: str | None = None
    repositoryId: str | None = None


class DiscoveryCandidate(BaseModel):
    candidate: Candidate

    discoveryEvidence: list[EvidenceItem] = Field(
        default_factory=list
    )


class DiscoveryCandidateList(BaseModel):
    candidates: list[DiscoveryCandidate] = Field(
        default_factory=list
    )


class DiscoveryDecision(BaseModel):
    enoughInformation: bool
    nextQuery: str | None = None


class TechnicalProfile(BaseModel):
    architecture: str | None = None

    parameterCount: int | str | None = None

    languages: list[str] = Field(
        default_factory=list
    )

    license: str | None = None

    # =================================================
    # MODEL RELATIONSHIP
    # =================================================

    baseModel: str | None = None

    baseModelRelation: str | None = None

    # =================================================
    # PERFORMANCE
    # =================================================

    reportedWer: str | None = None

    benchmarkDetails: str | None = None

    # =================================================
    # TRAINING
    # =================================================

    fineTuningSupport: str | None = None

    trainingDatasets: list[str] = Field(
        default_factory=list
    )

    # =================================================
    # INFERENCE
    # =================================================

    inferenceFramework: str | None = None

    inferenceRequirements: str | None = None

    hardwareRequirements: str | None = None


class VerificationResult(BaseModel):
    verified: bool

    missingFields: list[str] = Field(
        default_factory=list
    )

    issues: list[str] = Field(
        default_factory=list
    )


class StartScanRequest(BaseModel):
    query: str = (
        "Find automatic speech recognition "
        "models from recent sources."
    )

    discoveryConfig: dict | None = None

    researchConfig: dict | None = None