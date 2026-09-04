from app.services.echoforge.modelUploader import (
    uploadModel,
)


def testUpload(
    cacheName: str,
    modelName: str,
):

    print()
    print("=" * 60)
    print(f"UPLOADING: {modelName}")
    print("=" * 60)

    result = uploadModel(
        cacheName=cacheName,
        modelName=modelName,
    )

    print()
    print("UPLOAD RESULT:")
    print(result)


def main():

    # Model-specific example
    testUpload(
        cacheName="Qwen3-ASR-1.7B",
        modelName="Qwen3-ASR-1.7B",
    )

    # Generic Hugging Face example
    # testUpload(
    #     cacheName="nemotron-speech-streaming-en-0.6b",
    #     modelName="nemotron-speech-streaming-en-0.6b",
    # )


if __name__ == "__main__":
    main()
