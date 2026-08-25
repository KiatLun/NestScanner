from pydantic import BaseModel, Field
from typing import Any


class DiscoverySourceResult(BaseModel):
    source: str
    title: str
    url: str

    description: str | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)


class Candidate(BaseModel):
    name: str
    organisation: str | None = None
    sourceUrl: str | None = None
    reason: str | None = None
    candidate_type: str | None = None


class CandidateList(BaseModel):
    candidates: list[Candidate] = Field(default_factory=list)


class ModelProfile(BaseModel):
    name: str
    organisation: str | None = None
    releaseDate: str | None = None
    license: str | None = None
    architecture: str | None = None
    parameterCount: str | None = None

    languages: list[str] = Field(default_factory=list)

    reportedWer: str | None = None
    fineTuningSupport: str | None = None

    sourceUrls: list[str] = Field(default_factory=list)


class VerificationResult(BaseModel):
    verified: bool

    missingFields: list[str] = Field(default_factory=list)

    issues: list[str] = Field(default_factory=list)


class DiscoveryDecision(BaseModel):
    enoughInformation: bool
    nextQuery: str | None = None


class EvidenceItem(BaseModel):
    source: str
    title: str
    url: str
    description: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvidenceGroup(BaseModel):
    modelName: str
    organisation: str | None = None

    evidence: list[EvidenceItem] = Field(default_factory=list)
