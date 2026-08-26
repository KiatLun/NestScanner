import json

from agents.discovery import discoveryAgent


def main():
    state = {
        "query": (
            "Find recently released open-source " "automatic speech recognition models."
        )
    }

    result = discoveryAgent(state)

    print("\n=== CANDIDATES ===")

    print(
        json.dumps(
            result["candidates"],
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
