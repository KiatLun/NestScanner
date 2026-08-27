from models.schemas import Candidate, TechnicalProfile
from models.state import ScanState

candidate = Candidate(
    name="Example ASR",
    organisation="Example Lab",
)

profile = TechnicalProfile(
    name="Example ASR",
    architecture="CTC",
)

state: ScanState = {
    "query": "Find open-source ASR models",
    "current_model": candidate.model_dump(),
    "profile": profile.model_dump(),
}

print(state)
