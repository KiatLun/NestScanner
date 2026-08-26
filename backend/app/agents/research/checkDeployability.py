import json

from app.llm.client import getLLM

from app.tools.webSearch import (
    webSearch,
    deduplicateResults,
)

from app.tools.huggingFace import (
    searchHuggingFaceModels,
)

from app.tools.github import (
    searchGithubRepositories,
)


llm = getLLM()


def checkDeployability(
    candidate: dict,
    discoveryEvidence: list[dict],
) -> dict:
    """
    Gather deployability-related evidence and determine
    whether the model can be run locally.

    Local deployability requires BOTH:

    1. Public/downloadable model weights.
    2. A documented/public local inference path.

    Returns:
    {
        "isLocallyDeployable": bool,
        "evidence": list[dict]
    }
    """

    modelName = candidate.get(
        "name",
        "",
    )

    organisation = candidate.get(
        "organisation",
        "",
    )

    evidence = list(
        discoveryEvidence
    )

    # =================================================
    # 1. GATHER DEPLOYABILITY EVIDENCE
    # =================================================

    queries = [
        f'"{modelName}" model weights',
        f'"{modelName}" local inference',
        f'"{modelName}" download model',
        f'"{modelName}" from_pretrained',
    ]

    if organisation:
        queries.append(
            f'"{organisation}" "{modelName}" local inference'
        )

    for query in queries:
        try:
            results = webSearch(
                query,
                maxResults=5,
            )

            evidence.extend(
                results
            )

        except Exception as error:
            print(
                f"Deployability web search failed: "
                f"{query}"
            )

            print(error)

    try:
        hfResults = searchHuggingFaceModels(
            modelName,
            limit=10,
        )

        evidence.extend(
            hfResults
        )

    except Exception as error:
        print(
            "Deployability Hugging Face search failed."
        )

        print(error)

    try:
        githubResults = searchGithubRepositories(
            modelName,
            limit=5,
        )

        evidence.extend(
            githubResults
        )

    except Exception as error:
        print(
            "Deployability GitHub search failed."
        )

        print(error)

    evidence = deduplicateResults(
        evidence
    )

    # =================================================
    # 2. CHECK LOCAL DEPLOYABILITY
    # =================================================

    response = llm.invoke(f"""
You are checking whether an automatic speech recognition
model can be deployed locally.

Candidate:

{json.dumps(candidate, indent=2)}

Evidence:

{json.dumps(evidence, indent=2)}

A model is locally deployable ONLY if BOTH conditions
are supported:

1. Public/downloadable model weights are available.

2. The model can be run locally using publicly available
   code, libraries, frameworks, or documented inference
   instructions.

Evidence that may support local deployment includes:

- downloadable Hugging Face checkpoints
- from_pretrained(...)
- Transformers inference
- PyTorch inference
- ONNX inference
- inference scripts
- official GitHub inference code
- documented local execution instructions

The following are NOT enough by themselves:

- an API exists
- a research paper exists
- a GitHub repository exists
- source code exists but model weights do not
- weights exist but there is no usable local inference path

Use only supplied evidence.

Return ONLY valid JSON:

{{
    "isLocallyDeployable": true
}}

Do not include markdown.
Do not include code fences.
Do not include explanations outside the JSON.
""")

    try:
        result = json.loads(
            response.content
        )

    except json.JSONDecodeError:
        result = {
            "isLocallyDeployable": False
        }

    return {
        "isLocallyDeployable": result.get(
            "isLocallyDeployable",
            False,
        ),
        "evidence": evidence,
    }