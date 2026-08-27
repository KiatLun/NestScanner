import json

from app.agents.research.config import (
    ResearchConfig,
)

from app.agents.research.checkDeployability import (
    checkDeployability,
)

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"


def main():

    config = ResearchConfig()

    testCases = [
        {
            "name": "Mega-ASR",
            "candidate": {
                "name": "Mega-ASR",
                "organisation": None,
                "sourceUrl": ("https://github.com/" "xzf-thu/Mega-ASR"),
                "reason": ("Identifiable ASR model " "with public repository."),
                "candidateType": "model",
            },
            "discoveryEvidence": [
                {
                    "source": "github",
                    "title": "xzf-thu/Mega-ASR",
                    "url": ("https://github.com/" "xzf-thu/Mega-ASR"),
                    "description": (
                        "Mega-ASR repository. "
                        "Model weights are available "
                        "with inference and training code."
                    ),
                    "metadata": {},
                }
            ],
            "expected": True,
        },
        {
            "name": "Qwen3-ASR",
            "candidate": {
                "name": "Qwen3-ASR",
                "organisation": "Qwen",
                "sourceUrl": ("https://huggingface.co/" "Qwen/Qwen3-ASR-1.7B"),
                "reason": (
                    "Identifiable ASR model family " "with Hugging Face checkpoints."
                ),
                "candidateType": "model_family",
            },
            "discoveryEvidence": [
                {
                    "source": "huggingface",
                    "title": ("Qwen/Qwen3-ASR-1.7B"),
                    "url": ("https://huggingface.co/" "Qwen/Qwen3-ASR-1.7B"),
                    "description": (
                        "Qwen3-ASR model checkpoint " "hosted on Hugging Face."
                    ),
                    "metadata": {},
                }
            ],
            "expected": True,
        },
        {
            "name": "Cohere Transcribe",
            "candidate": {
                "name": ("cohere-transcribe-03-2026"),
                "organisation": "Cohere",
                "sourceUrl": None,
                "reason": ("Identifiable Cohere ASR model."),
                "candidateType": "model",
            },
            "discoveryEvidence": [
                {
                    "source": "web",
                    "title": ("Cohere Transcribe"),
                    "url": "https://example.com/cohere",
                    "description": (
                        "Cohere released its " "Transcribe speech recognition " "model."
                    ),
                    "metadata": {},
                }
            ],
            "expected": True,
        },
        {
            "name": "GPT-Transcribe",
            "candidate": {
                "name": "GPT-Transcribe",
                "organisation": "OpenAI",
                "sourceUrl": None,
                "reason": ("Identifiable speech-to-text model."),
                "candidateType": "model",
            },
            "discoveryEvidence": [
                {
                    "source": "web",
                    "title": "GPT-Transcribe",
                    "url": "https://example.com/gpt",
                    "description": (
                        "GPT-Transcribe is an " "OpenAI speech-to-text model."
                    ),
                    "metadata": {},
                }
            ],
            "expected": False,
        },
    ]

    passed = 0

    for index, testCase in enumerate(
        testCases,
        start=1,
    ):

        print("\n" + "=" * 70)

        print(f"TEST {index}: " f"{testCase['name']}")

        print("=" * 70)

        result = checkDeployability(
            testCase["candidate"],
            testCase["discoveryEvidence"],
            config,
        )

        print("\n=== RESULT ===")

        print(
            json.dumps(
                result,
                indent=2,
            )
        )

        actual = result.get("isLocallyDeployable")

        expected = testCase["expected"]

        print(f"\nExpected: {expected}")

        print(f"Actual:   {actual}")

        if actual == expected:

            passed += 1

            print(f"{GREEN}" "PASS" f"{RESET}")

        else:
            print(f"{RED}" "FAIL" f"{RESET}")

    print("\n" + "=" * 70)

    print("FINAL SUMMARY")

    print("=" * 70)

    print(f"Passed: " f"{passed}/{len(testCases)}")

    if passed == len(testCases):

        print(f"{GREEN}" "ALL TESTS PASSED" f"{RESET}")

    else:
        print(f"{RED}" "SOME TESTS FAILED" f"{RESET}")


if __name__ == "__main__":
    main()
