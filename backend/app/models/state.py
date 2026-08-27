from typing import TypedDict


class ScanState(TypedDict, total=False):
    query: str
    candidates: list[dict]
    researchResults: list[dict]