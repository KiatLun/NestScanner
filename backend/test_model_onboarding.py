import json

from app.services.onboarding.modelOnboarding import (
    onboardModel,
)


def main():
    result = onboardModel(
        modelName="whisper-tiny",
        sourceType="huggingface",
        source="openai/whisper-tiny",
        cacheName="onboarding-whisper-test",
    )

    print("\n=== ONBOARDING RESULT ===")

    print(
        json.dumps(
            result,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
