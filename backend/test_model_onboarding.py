import json

from app.services.onboarding.modelOnboarding import (
    onboardModel,
)


def main():

    result = onboardModel(
        modelName="whisper-base",
        sourceType="huggingface",
        source="openai/whisper-base",
        cacheName="onboarding-whisper-base-test",
    )

    # result = onboardModel(
    #     modelName="silero",
    #     sourceType="github",
    #     source="https://github.com/snakers4/silero-models",
    # )

    print("\n=== ONBOARDING RESULT ===")

    print(
        json.dumps(
            result,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
