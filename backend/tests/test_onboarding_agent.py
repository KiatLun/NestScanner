from app.agents.onboarding import (
    onboardingAgent,
)


def testModel(
    researchResult: dict,
):

    print()
    print("=" * 70)
    print(f"TESTING: " f"{researchResult['modelName']}")
    print("=" * 70)

    result = onboardingAgent(researchResult)

    print()
    print("RESULT:")
    print(result)

    return result


def main():

    results = []

    # ========================================
    # Test 1:
    # New model that generic HF can handle
    # ========================================

    results.append(
        testModel(
            {
                "modelName": "whisper-base",
                "sourceType": "huggingface",
                "source": "openai/whisper-base",
                "researchEvidence": [],
                "technicalProfile": {
                    "architecture": "Whisper",
                },
            }
        )
    )

    # ========================================
    # Test 2:
    # New model with no current downloader
    # ========================================

    results.append(
        testModel(
            {
                "modelName": "test-new-github-asr",
                "sourceType": "github",
                "source": ("some-org/" "test-new-github-asr"),
                "researchEvidence": [],
                "technicalProfile": {},
            }
        )
    )

    # ========================================
    # Summary
    # ========================================

    print()
    print("=" * 70)
    print("ONBOARDING AGENT SUMMARY")
    print("=" * 70)

    for result in results:

        print()
        print(f"Model: " f"{result['modelName']}")

        print(f"Status: " f"{result['status']}")

        if result["status"] == "completed":

            print(f"Downloader: " f"{result['downloader']}")

            print(f"Cache: " f"{result['cacheName']}")

            print(f"ClearML ID: " f"{result['clearmlModelId']}")


if __name__ == "__main__":
    main()
