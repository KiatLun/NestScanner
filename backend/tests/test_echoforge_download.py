from app.services.echoforge.modelInfoReader import (
    getAllModelInfo,
)

from app.services.echoforge.downloadResolver import (
    resolveDownloader,
)

from app.services.echoforge.modelDownloader import (
    downloadModel,
)


def testModel(
    modelName: str,
    sourceType: str,
    source: str,
):

    print()
    print("=" * 60)
    print(f"TESTING: {modelName}")
    print("=" * 60)

    modelInfo = getAllModelInfo()

    downloader = resolveDownloader(
        modelName=modelName,
        sourceType=sourceType,
        source=source,
        modelInfo=modelInfo,
    )

    print(
        "RESOLVED DOWNLOADER:",
        downloader,
    )

    if not downloader:
        print("No downloader found.")
        return

    result = downloadModel(
        downloader=downloader,
        modelName=modelName,
        sourceType=sourceType,
        source=source,
    )

    print()
    print("DOWNLOAD RESULT:")
    print(result)


def main():

    # ----------------------------------------
    # Test 1: model-specific
    # ----------------------------------------

    testModel(
        modelName="silero",
        sourceType="github",
        source="silero",
    )

    # ----------------------------------------
    # Test 2: generic Hugging Face
    # ----------------------------------------

    testModel(
        modelName=("nemotron-speech-streaming-en-0.6b"),
        sourceType="huggingface",
        source=("nvidia/" "nemotron-speech-streaming-en-0.6b"),
    )


if __name__ == "__main__":
    main()
