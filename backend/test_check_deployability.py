import json

from app.agents.research.checkDeployability import (
    checkDeployability,
)


def runTest(
    name: str,
    researchInput: dict,
    expectedDeployable: bool,
):
    result = checkDeployability(
        researchInput["candidate"],
        researchInput["discoveryEvidence"],
    )

    print(
        "\n"
        + "=" * 60
    )

    print(
        f"TEST: {name}"
    )

    print(
        "=" * 60
    )

    print(
        json.dumps(
            result,
            indent=2,
        )
    )

    actualDeployable = result.get(
        "isLocallyDeployable",
        False,
    )

    if actualDeployable == expectedDeployable:
        print(
            "\nPASS"
        )
    else:
        print(
            "\nFAIL"
        )

    print(
        f"Expected isLocallyDeployable: "
        f"{expectedDeployable}"
    )

    print(
        f"Actual isLocallyDeployable: "
        f"{actualDeployable}"
    )


def main():

    # =================================================
    # POSITIVE TEST
    # Cohere Transcribe should be locally deployable
    # =================================================

    cohereInput = {
        "candidate": {
            "name": "cohere-transcribe-03-2026",
            "organisation": "Cohere",
            "sourceUrl": (
                "https://techcrunch.com/2026/03/26/"
                "cohere-launches-an-open-source-voice-model-"
                "specifically-for-transcription/"
            ),
            "reason": (
                "Cohere open-source voice model for "
                "transcription released March 2026."
            ),
            "candidateType": "model",
        },
        "discoveryEvidence": [
            {
                "source": "web",
                "title": (
                    "Cohere launches an open source voice "
                    "model specifically for transcription"
                ),
                "url": (
                    "https://techcrunch.com/2026/03/26/"
                    "cohere-launches-an-open-source-voice-model-"
                    "specifically-for-transcription/"
                ),
                "description": (
                    "The model is open source and intended "
                    "for users who want to self-host it on "
                    "consumer-grade GPUs."
                ),
                "metadata": {},
            }
        ],
    }

    # =================================================
    # NEGATIVE TEST
    # GPT-Transcribe is API-accessed, not local weights
    # =================================================

    gptTranscribeInput = {
        "candidate": {
            "name": "GPT-Transcribe",
            "organisation": "OpenAI",
            "sourceUrl": (
                "https://spokenly.app/blog/"
                "gpt-transcribe"
            ),
            "reason": (
                "OpenAI speech-to-text model for "
                "transcription."
            ),
            "candidateType": "model",
        },
        "discoveryEvidence": [
            {
                "source": "web",
                "title": (
                    "GPT-Transcribe: OpenAI's New "
                    "Speech-to-Text Model"
                ),
                "url": (
                    "https://spokenly.app/blog/"
                    "gpt-transcribe"
                ),
                "description": (
                    "GPT-Transcribe is an OpenAI "
                    "speech-to-text model available for "
                    "audio transcription."
                ),
                "metadata": {},
            }
        ],
    }

    runTest(
        "Cohere Transcribe - Positive",
        cohereInput,
        expectedDeployable=True,
    )

    runTest(
        "GPT-Transcribe - Negative",
        gptTranscribeInput,
        expectedDeployable=False,
    )


if __name__ == "__main__":
    main()