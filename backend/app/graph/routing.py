from app.config.settings import MAX_RESEARCH_RETRIES
from app.models.state import ScanState


def verification_router(state: ScanState) -> str:
    """
    Decide whether to finish or send the model back
    to the Research Agent.
    """

    if state.get("verified"):
        return "done"

    if state.get("retryCount", 0) >= MAX_RESEARCH_RETRIES:
        return "done"

    return "research_again"
