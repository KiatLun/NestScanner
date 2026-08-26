import json

from app.agents.research.checkRecency import (
    checkRecency,
)


GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"


def main():
    testCases = [
        {
            "name": "GPT-Transcribe",
            "expectedRecent": True,
            "input": {
                "candidate": {
                    "name": "GPT-Transcribe",
                    "organisation": "OpenAI",
                    "sourceUrl": "https://spokenly.app/blog/gpt-transcribe",
                    "reason": (
                        "OpenAI speech-to-text model released "
                        "July 28 2026."
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
                            "speech-to-text model released on "
                            "July 28, 2026."
                        ),
                        "metadata": {},
                    }
                ],
            },
        },
        {
            "name": "diffusion-gemma-asr-small",
            "expectedRecent": True,
            "input": {
                "candidate": {
                    "name": "diffusion-gemma-asr-small",
                    "organisation": None,
                    "sourceUrl": (
                        "https://www.nextpulse.site/2026/07/"
                        "revolutionizing-multilingual-asr.html"
                    ),
                    "reason": (
                        "Open-source diffusion ASR model "
                        "released July 2026."
                    ),
                    "candidateType": "model",
                },
                "discoveryEvidence": [
                    {
                        "source": "web",
                        "title": (
                            "Revolutionizing Multilingual ASR"
                        ),
                        "url": (
                            "https://www.nextpulse.site/2026/07/"
                            "revolutionizing-multilingual-asr.html"
                        ),
                        "description": (
                            "July 5, 2026 - Interfaze has released "
                            "diffusion-gemma-asr-small."
                        ),
                        "metadata": {},
                    }
                ],
            },
        },
        {
            "name": "Qwen3-ASR",
            "expectedRecent": False,
            "input": {
                "candidate": {
                    "name": "Qwen3-ASR",
                    "organisation": "Qwen",
                    "sourceUrl": (
                        "https://github.com/QwenLM/Qwen3-ASR"
                    ),
                    "reason": (
                        "Open-source ASR series from Qwen."
                    ),
                    "candidateType": "model_family",
                },
                "discoveryEvidence": [
                    {
                        "source": "web",
                        "title": "Qwen3-ASR-1.7B",
                        "url": (
                            "https://qwen-image-2512.com/blog/"
                            "qwen3-asr-1.7b-complete-guide-en"
                        ),
                        "description": (
                            "Qwen3-ASR-1.7B was released on "
                            "January 29, 2026."
                        ),
                        "metadata": {},
                    }
                ],
            },
        },
        {
            "name": "Mega-ASR",
            "expectedRecent": False,
            "input": {
                "candidate": {
                    "name": "Mega-ASR",
                    "organisation": None,
                    "sourceUrl": (
                        "https://github.com/xzf-thu/Mega-ASR"
                    ),
                    "reason": (
                        "Foundation ASR project released "
                        "in May 2026."
                    ),
                    "candidateType": "model",
                },
                "discoveryEvidence": [
                    {
                        "source": "web",
                        "title": "GitHub - xzf-thu/Mega-ASR",
                        "url": (
                            "https://github.com/xzf-thu/Mega-ASR"
                        ),
                        "description": (
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
            "expectedRecent": False,
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
                        "Cohere transcription model released "
                        "March 2026."
                    ),
                    "candidateType": "model",
                },
                "discoveryEvidence": [
                    {
                        "source": "web",
                        "title": (
                            "Cohere launches an open source voice model"
                        ),
                        "url": (
                            "https://techcrunch.com/2026/03/26/"
                            "cohere-launches-an-open-source-voice-model-"
                            "specifically-for-transcription/"
                        ),
                        "description": (
                            "March 30, 2026 - CohereLabs has released "
                            "the cohere-transcribe-03-2026 ASR model."
                        ),
                        "metadata": {},
                    }
                ],
            },
        },
    ]

    passedCount = 0

    for testCase in testCases:
        result = checkRecency(
            testCase["input"]["candidate"],
            testCase["input"]["discoveryEvidence"],
            days=60,
        )

        actualRecent = result.get(
            "isRecent",
            False,
        )

        passed = (
            actualRecent
            == testCase["expectedRecent"]
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
            f"{testCase['expectedRecent']}"
        )

        print(
            f"Actual: "
            f"{actualRecent}"
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