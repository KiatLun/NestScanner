import json

from agents.research import research_agent


def main():
    state = {
        "currentModel": {
            "name": "Whisper",
            "organisation": "OpenAI",
            "sourceUrl": "https://github.com/openai/whisper",
            "reason": "Open-source ASR model",
        },
        "missing_fields": [],
    }

    result = research_agent(state)

    print("\n=== MODEL PROFILE ===")
    print(
        json.dumps(
            result["profile"],
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
