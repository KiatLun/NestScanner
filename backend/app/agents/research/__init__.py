from app.agents.research.agent import (
    researchAgent,
)


def researchAgent(
    state: dict,
) -> dict:

    candidates = state.get(
        "candidates",
        [],
    )

    researchResults = []

    for researchInput in candidates:

        result = researchAgent(researchInput)

        researchResults.append(result)

    return {"researchResults": researchResults}
