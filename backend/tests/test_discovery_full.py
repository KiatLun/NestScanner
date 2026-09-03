import json

from app.agents.discovery import discoveryAgent


def main():
    state = {
        "query": (
            "Find recently released open-source " "automatic speech recognition models."
        )
    }
    result = discoveryAgent(state)

    print("\n" + "=" * 60)
    print("FINAL DISCOVERY OUTPUT")
    print("=" * 60)

    print("\nCandidates:")
    print(
        json.dumps(
            result.get("candidates", []),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
