from pydantic import BaseModel, Field
from typing import Any


class EvidenceItem(BaseModel):
    source: str
    title: str
    url: str

    description: str | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)


class Candidate(BaseModel):
    name: str
    organisation: str | None = None
    sourceUrl: str | None = None
    candidateType: str | None = None


class DiscoveryCandidate(BaseModel):
    candidate: Candidate

    discoveryEvidence: list[EvidenceItem] = Field(default_factory=list)


class DiscoveryCandidateList(BaseModel):
    candidates: list[DiscoveryCandidate] = Field(default_factory=list)


class DiscoveryDecision(BaseModel):
    enoughInformation: bool
    nextQuery: str | None = None


class TechnicalProfile(BaseModel):
    architecture: str | None = None
    parameterCount: str | None = None
    languages: list[str] = Field(default_factory=list)
    reportedWer: str | None = None
    fineTuningSupport: str | None = None
    license: str | None = None


class VerificationResult(BaseModel):
    verified: bool

    missingFields: list[str] = Field(default_factory=list)

    issues: list[str] = Field(default_factory=list)


class StartScanRequest(BaseModel):
    query: str = "Find automatic speech recognition " "models from recent sources."

    discoveryConfig: dict | None = None
    researchConfig: dict | None = None
