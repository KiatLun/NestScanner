from app.services.echoforge.modelOnboarding import (
    onboardModel,
)


def testModel(
    modelName: str,
    sourceType: str,
    source: str,
):

    print()
    print("#" * 70)
    print(f"TESTING MODEL: {modelName}")
    print("#" * 70)

    try:
        result = onboardModel(
            modelName=modelName,
            sourceType=sourceType,
            source=source,
        )

        print()
        print("FINAL RESULT:")
        print(result)

        return result

    except Exception as error:

        print()
        print("ONBOARDING FAILED:")
        print(error)

        return {
            "modelName": modelName,
            "status": "failed",
            "error": str(error),
        }


def main():

    results = []

    # ----------------------------------------
    # 1. Model-specific downloader
    # ----------------------------------------

    results.append(
        testModel(
            modelName="silero",
            sourceType="github",
            source="silero",
        )
    )

    # ----------------------------------------
    # 2. Generic Hugging Face downloader
    # ----------------------------------------

    results.append(
        testModel(
            modelName=("nemotron-speech-streaming-en-0.6b"),
            sourceType="huggingface",
            source=("nvidia/" "nemotron-speech-streaming-en-0.6b"),
        )
    )

    # ----------------------------------------
    # Summary
    # ----------------------------------------

    print()
    print("=" * 70)
    print("ONBOARDING SUMMARY")
    print("=" * 70)

    for result in results:

        print()

        print(f"Model: " f"{result['modelName']}")

        print(f"Status: " f"{result['status']}")

        if result["status"] == "completed":

            print(f"Downloader: " f"{result['downloader']}")

            print(f"Cache: " f"{result['cacheName']}")

            print(f"ClearML ID: " f"{result['clearmlModelId']}")

        else:

            print(f"Error: " f"{result['error']}")


if __name__ == "__main__":
    main()
