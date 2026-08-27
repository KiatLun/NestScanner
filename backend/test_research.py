import json

from app.agents.research.agent import researchAgent


def main():
    with open(
        "app/agents/discovery/sampleOutput.txt",
        "r",
        encoding="utf-8",
    ) as file:
        discoveryOutput = json.load(file)

    candidates = discoveryOutput[
        "candidates"
    ]

    print(
        f"\nFound {len(candidates)} "
        "Discovery candidates."
    )

    researchInput = candidates[1]

    result = researchAgent(
        researchInput
    )

    print(
        "\n=== RESEARCH RESULT ==="
    )

    print(
        json.dumps(
            result,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()