import json

from app.agents.research.agent import researchAgent

from app.agents.research.config import (
    ResearchConfig,
)


def main():

    config = ResearchConfig(
        recencyWindowDays=180,
        maxRecencySearches=2,
        recencyResultsPerSearch=3,
        maxDeployabilitySearches=2,
        deployabilityResultsPerSearch=3,
        verbose=True,
    )

    with open(
        "app/agents/discovery/sampleOutput.txt",
        "r",
        encoding="utf-8",
    ) as file:
        discoveryOutput = json.load(file)

    candidates = discoveryOutput["candidates"]

    print(f"\nFound {len(candidates)} " "Discovery candidates.")

    researchInput = candidates[1]

    result = researchAgent(
        researchInput,
        config,
    )

    print("\n=== RESEARCH RESULT ===")

    print(
        json.dumps(
            result,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
