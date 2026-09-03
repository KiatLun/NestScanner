from app.services.echoforge.modelInfoReader import getAllModelInfo
from app.services.echoforge.downloadResolver import resolveDownloader


def main():
    modelInfo = getAllModelInfo()

    tests = [
        {
            "modelName": "whisper-tiny",
            "sourceType": "huggingface",
            "source": "openai/whisper-tiny",
        },
        {
            "modelName": "silero",
            "sourceType": "github",
            "source": "silero",
        },
        {
            "modelName": "nemotron-speech-streaming-en-0.6b",
            "sourceType": "huggingface",
            "source": "nvidia/nemotron-speech-streaming-en-0.6b",
        },
    ]

    for test in tests:
        result = resolveDownloader(
            modelName=test["modelName"],
            sourceType=test["sourceType"],
            source=test["source"],
            modelInfo=modelInfo,
        )

        print(result)
        print("MODEL:", test["modelName"])
        print("SOURCE TYPE:", test["sourceType"])
        print("SOURCE:", test["source"])
        print("RESOLVED:", result)


if __name__ == "__main__":
    main()
