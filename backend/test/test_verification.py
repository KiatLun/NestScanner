import json

from agents.verification import verification_agent


def main():
    state = {
        "profile": {
            "name": "Example ASR",
            "organisation": "Example Lab",
            "release_date": "2026",
            "license": None,
            "architecture": "CTC",
            "parameter_count": "1B",
            "languages": ["English"],
            "reported_wer": "5.0% on ExampleSet",
            "fine_tuning_support": "Supported",
            "sourceUrl": ["https://example.com/model"],
        },
        "retry_count": 0,
    }

    result = verification_agent(state)

    print("\n=== VERIFICATION RESULT ===")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
