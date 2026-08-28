import json

from app.services.echoforge.modelDeployment import (
    prepareModel,
)


def main():

    result = prepareModel(
        repoId="nvidia/nemotron-speech-streaming-en-0.6b",
        cacheName="nemotron-speech-streaming-en-0.6b",
        modelName="nemotron-speech-streaming-en-0.6b",
    )

    print("\n=== MODEL DEPLOYMENT RESULT ===")

    print(
        json.dumps(
            result,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
