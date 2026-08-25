import json

from helper.evidenceMatcher import (
    groupModelEvidence,
)


def main():

    # Fake discovery results.
    # The first three should ideally be grouped together.
    # The fourth should remain separate.
    results = [
        {
            "source": "huggingface",
            "title": "Qwen/Qwen3-ASR-1.7B",
            "url": "https://huggingface.co/Qwen/Qwen3-ASR-1.7B",
            "description": None,
            "metadata": {
                "organisation": "Qwen",
                "pipeline_tag": "automatic-speech-recognition",
            },
        },
        {
            "source": "github",
            "title": "QwenLM/Qwen3-ASR",
            "url": "https://github.com/QwenLM/Qwen3-ASR",
            "description": (
                "Official repository for the Qwen3-ASR "
                "speech recognition model family."
            ),
            "metadata": {
                "organisation": "QwenLM",
            },
        },
        {
            "source": "arxiv",
            "title": ("Qwen3-ASR: Multilingual Automatic " "Speech Recognition"),
            "url": "https://arxiv.org/abs/1234.5678",
            "description": ("A paper describing the Qwen3-ASR " "model family."),
            "metadata": {"authors": ["Example Author"]},
        },
        {
            "source": "github",
            "title": "example-org/completely-different-asr",
            "url": ("https://github.com/" "example-org/completely-different-asr"),
            "description": ("A separate automatic speech " "recognition project."),
            "metadata": {"organisation": "example-org"},
        },
    ]

    print("\n=== INPUT RESULTS ===")

    print(
        json.dumps(
            results,
            indent=2,
        )
    )

    groups = groupModelEvidence(results)

    print("\n" + "=" * 60)
    print("EVIDENCE GROUPS")
    print("=" * 60)

    print(
        json.dumps(
            groups,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
