from typing import TypedDict


class ScanState(TypedDict, total=False):
    query: str
    scanId: int

    discoveryConfig: dict
    researchConfig: dict

    candidates: list[dict]
    researchResults: list[dict]
