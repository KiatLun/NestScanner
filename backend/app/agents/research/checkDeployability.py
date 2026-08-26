import json

from app.llm.client import getLLM
from app.tools.webSearch import (
    webSearch,
    deduplicateResults,
)


llm = getLLM()


def checkDeployability(
    candidate: dict,
    discoveryEvidence: list[dict],
    maxSearches: int = 3,
) -> dict:
    """
    Determine whether a model can be deployed locally.

    Local deployability requires:
    1. Public/downloadable weights.
    2. A usable local inference path.
    """

    evidence = list(
        discoveryEvidence
    )

    searchCount = 0

    while True:

        decision = evaluateDeployability(
            candidate,
            evidence,
        )

        if decision.get(
            "enoughInformation",
            False,
        ):
            return {
                "isLocallyDeployable": decision.get(
                    "isLocallyDeployable",
                    False,
                ),
                "evidence": evidence,
            }

        if searchCount >= maxSearches:
            return {
                "isLocallyDeployable": False,
                "evidence": evidence,
            }

        nextQuery = decision.get(
            "nextQuery"
        )

        if not nextQuery:
            return {
                "isLocallyDeployable": False,
                "evidence": evidence,
            }

        print(
            f"\nDeployability search "
            f"{searchCount + 1}: "
            f"{nextQuery}"
        )

        try:
            results = webSearch(
                nextQuery,
                maxResults=5,
            )

            evidence.extend(
                results
            )

            evidence = deduplicateResults(
                evidence
            )

        except Exception as error:
            print(
                f"Deployability search failed: "
                f"{nextQuery}"
            )

            print(error)

        searchCount += 1


def evaluateDeployability(
    candidate: dict,
    evidence: list[dict],
) -> dict:
    """
    Decide whether current evidence is enough to establish
    local deployability.

    If not, generate one targeted search query.
    """

    response = llm.invoke(f"""
You are checking whether an automatic speech recognition
model can be deployed locally.

Candidate:

{json.dumps(candidate, indent=2)}

Evidence:

{json.dumps(evidence, indent=2)}

A model is locally deployable ONLY if BOTH conditions
are supported:

1. Public/downloadable model weights exist.

2. There is a usable local inference path.

Examples of valid local inference evidence:

- Hugging Face checkpoints
- from_pretrained(...)
- Transformers
- PyTorch
- ONNX
- inference scripts
- official GitHub inference code
- documented local execution instructions

The following are NOT sufficient by themselves:

- API access
- research paper
- GitHub repository without weights
- weights without inference instructions


IF ENOUGH INFORMATION EXISTS

Return:

{{
    "enoughInformation": true,
    "isLocallyDeployable": true,
    "nextQuery": null
}}

or:

{{
    "enoughInformation": true,
    "isLocallyDeployable": false,
    "nextQuery": null
}}


IF MORE INFORMATION IS NEEDED

Generate ONE highly targeted query that would best
resolve the missing information.

Examples:

"Qwen3-ASR Hugging Face weights inference"

"Cohere Transcribe local inference"

"GPT-Transcribe downloadable weights"

Return:

{{
    "enoughInformation": false,
    "isLocallyDeployable": false,
    "nextQuery": "targeted query"
}}

Return ONLY valid JSON.
Do not include markdown.
""")

    try:
        return json.loads(
            response.content
        )

    except json.JSONDecodeError:
        return {
            "enoughInformation": False,
            "isLocallyDeployable": False,
            "nextQuery": None,
        }