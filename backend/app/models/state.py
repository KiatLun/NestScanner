from typing import TypedDict


class ScanState(TypedDict, total=False):
    query: str

    candidates: list[dict]
    currentModel: dict

    profile: dict

    verified: bool
    missingFields: list[str]
    issues: list[str]

    retryCount: int
