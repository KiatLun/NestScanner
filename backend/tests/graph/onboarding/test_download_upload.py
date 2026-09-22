from pprint import pprint

from app.graph.onboarding.workflow import (
    runOnboardingWorkflow,
)

from tests.fixtures.researchAgentOutput import (
    researchAgentOutput,
)

# ============================================================
# Choose which models to test
# ============================================================

# Refer to the onboardingFixtures to view expected behaviours
modelsToTest = [
    # "qwen3-asr-1.7b",  # Generic Hugging Face
    # "mega-asr",  # Generic Hugging Face
    # "fun-asr-nano-2512",  # Generic Hugging Face
    "sensevoice-small",  # Generic Hugging Face
    # "voxtral-mini-3b-2507",  # Model-specific
    # "whisper-medium",  # Model-specific
    "whisper-small",  # Model-specific
    # "voxtral-mini-4b-realtime-2602",  # Model-specific
    # "silero-vad",  # Repository-based model
    "deepspeech-0.9.3",  # Cant for both model-specific and generic HF
    # "example-direct-asr",  # Cant for both model-specific and generic HF
]


def main():

    print()
    print("=" * 60)
    print("ONBOARDING WORKFLOW TEST")
    print("=" * 60)

    for modelKey in modelsToTest:

        print()
        print("-" * 60)
        print(f"Testing: {modelKey}")
        print("-" * 60)

        researchResult = researchAgentOutput[modelKey]

        result = runOnboardingWorkflow(researchResult)

        print()
        print("=" * 60)
        print("ONBOARDING RESULT")
        print("=" * 60)

        pprint(
            result,
            sort_dicts=False,
        )


if __name__ == "__main__":
    main()
