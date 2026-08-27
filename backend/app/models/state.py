from typing import TypedDict


class ScanState(TypedDict, total=False):
    query: str

    runId: int

    candidates: list[dict]
    researchResults: list[dict]
