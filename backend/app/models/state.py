from typing import TypedDict


class ScanState(TypedDict, total=False):
    query: str

    scanId: int

    candidates: list[dict]
    researchResults: list[dict]
