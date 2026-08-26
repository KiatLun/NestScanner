import json

from app.agents.research.checkDeployability import (
    checkDeployability,
)


GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"


def main():
    testCases = [
        {
            "name": "Mega-ASR",
            "expectedDeployable": True,
            "input": {
                "candidate": {
                    "name": "Mega-ASR",
                    "organisation": None,
                    "sourceUrl": "https://github.com/xzf-thu/Mega-ASR",
                    "reason": (
                        "Foundation ASR project with released "
                        "inference/training codebase and model weights."
                    ),
                    "candidateType": "model",
                },
                "discoveryEvidence": [
                    {
                        "source": "web",
                        "title": "GitHub - xzf-thu/Mega-ASR",
                        "url": "https://github.com/xzf-thu/Mega-ASR",
                        "description": (
                            "May 20, 2026: We release the Mega-ASR "
                            "Inference and Training Codebase. "
                            "May 19, 2026: Mega-ASR model weights "
                            "are now available on Hugging Face."
                        ),
                        "metadata": {},
                    }
                ],
            },
        },
        {
            "name": "cohere-transcribe-03-2026",
            "expectedDeployable": True,
            "input": {
                "candidate": {
                    "name": "cohere-transcribe-03-2026",
                    "organisation": "Cohere",
                    "sourceUrl": (
                        "https://techcrunch.com/2026/03/26/"
                        "cohere-launches-an-open-source-voice-model-"
                        "specifically-for-transcription/"
                    ),
                    "reason": (
                        "Cohere open-source transcription model."
                    ),
                    "candidateType": "model",
                },
                "discoveryEvidence": [
                    {
                        "source": "web",
                        "title": (
                            "Cohere launches an open source voice model "
                            "specifically for transcription"
                        ),
                        "url": (
                            "https://techcrunch.com/2026/03/26/"
                            "cohere-launches-an-open-source-voice-model-"
                            "specifically-for-transcription/"
                        ),
                        "description": (
                            "The model is meant for use with "
                            "consumer-grade GPUs for those who "
                            "want to self-host it."
                        ),
                        "metadata": {},
                    }
                ],
            },
        },
        {
            "name": "Qwen3-ASR",
            "expectedDeployable": True,
            "input": {
                "candidate": {
                    "name": "Qwen3-ASR",
                    "organisation": "Qwen",
                    "sourceUrl": "https://github.com/QwenLM/Qwen3-ASR",
                    "reason": "Open-source ASR series from Qwen.",
                    "candidateType": "model_family",
                },
                "discoveryEvidence": [
                    {
                        "source": "huggingface",
                        "title": "Qwen/Qwen3-ASR-1.7B",
                        "url": (
                            "https://huggingface.co/"
                            "Qwen/Qwen3-ASR-1.7B"
                        ),
                        "description": None,
                        "metadata": {
                            "organisation": "Qwen",
                            "pipelineTag": (
                                "automatic-speech-recognition"
                            ),
                            "tags": [
                                "safetensors",
                                "qwen3_asr",
                                "automatic-speech-recognition",
                                "license:apache-2.0",
                            ],
                        },
                    }
                ],
            },
        },
        {
            "name": "GPT-Transcribe",
            "expectedDeployable": False,
            "input": {
                "candidate": {
                    "name": "GPT-Transcribe",
                    "organisation": "OpenAI",
                    "sourceUrl": (
                        "https://spokenly.app/blog/"
                        "gpt-transcribe"
                    ),
                    "reason": (
                        "OpenAI speech-to-text model "
                        "for transcription."
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
                            "GPT-Transcribe is OpenAI's "
                            "speech-to-text model."
                        ),
                        "metadata": {},
                    }
                ],
            },
        },
    ]

    passedCount = 0

    for testCase in testCases:
        result = checkDeployability(
            testCase["input"]["candidate"],
            testCase["input"]["discoveryEvidence"],
        )

        actualDeployable = result.get(
            "isLocallyDeployable",
            False,
        )

        passed = (
            actualDeployable
            == testCase["expectedDeployable"]
        )

        if passed:
            passedCount += 1

        color = GREEN if passed else RED
        status = "PASS" if passed else "FAIL"

        print(
            "\n"
            + "=" * 70
        )

        print(
            f"TEST: {testCase['name']}"
        )

        print(
            "=" * 70
        )

        print(
            json.dumps(
                result,
                indent=2,
            )
        )

        print(
            f"\nExpected: "
            f"{testCase['expectedDeployable']}"
        )

        print(
            f"Actual: "
            f"{actualDeployable}"
        )

        print(
            f"\n{color}{status}{RESET}"
        )

    total = len(
        testCases
    )

    print(
        "\n"
        + "=" * 70
    )

    if passedCount == total:
        print(
            f"{GREEN}"
            f"ALL TESTS PASSED "
            f"({passedCount}/{total})"
            f"{RESET}"
        )
    else:
        print(
            f"{RED}"
            f"{passedCount}/{total} "
            f"TESTS PASSED"
            f"{RESET}"
        )


if __name__ == "__main__":
    main()