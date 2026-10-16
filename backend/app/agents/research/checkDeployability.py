import json

from huggingface_hub import (
    HfApi,
    hf_hub_download,
)

from app.llm.client import getLLM

from app.agents.research.config import (
    ResearchConfig,
)

from app.tools.webSearch import (
    webSearch,
    deduplicateResults,
)


api = HfApi()
llm = getLLM()


# =====================================================
# HUGGING FACE EVIDENCE
# =====================================================

def getHuggingFaceEvidence(
    candidate: dict,
) -> list[dict]:
    """
    Retrieve additional information directly from the
    exact Hugging Face model repository.

    This does not download model weights.

    It retrieves:

    - repository metadata
    - repository files
    - model card / README

    The repository ID from the candidate is treated as
    the exact model identity.
    """

    repositoryId = candidate.get(
        "repositoryId"
    )

    if not repositoryId:
        return []

    evidence = []

    modelUrl = (
        f"https://huggingface.co/{repositoryId}"
    )


    # =================================================
    # MODEL INFORMATION
    # =================================================

    try:

        modelInfo = api.model_info(
            repo_id=repositoryId,
            files_metadata=True,
        )

        siblings = getattr(
            modelInfo,
            "siblings",
            [],
        )

        files = []

        for sibling in siblings:

            filename = getattr(
                sibling,
                "rfilename",
                None,
            )

            if filename:
                files.append(
                    filename
                )


        evidence.append(
            {
                "source": "huggingface",

                "title": repositoryId,

                "url": modelUrl,

                "description": (
                    "Hugging Face model repository metadata."
                ),

                "metadata": {
                    "repositoryId": repositoryId,

                    "pipelineTag": getattr(
                        modelInfo,
                        "pipeline_tag",
                        None,
                    ),

                    "downloads": getattr(
                        modelInfo,
                        "downloads",
                        None,
                    ),

                    "likes": getattr(
                        modelInfo,
                        "likes",
                        None,
                    ),

                    "tags": getattr(
                        modelInfo,
                        "tags",
                        [],
                    ),

                    "files": files,
                },
            }
        )

    except Exception as error:

        print(
            "Failed to retrieve Hugging Face "
            f"metadata for {repositoryId}:"
        )

        print(error)


    # =================================================
    # MODEL CARD / README
    # =================================================

    try:

        readmePath = hf_hub_download(
            repo_id=repositoryId,
            filename="README.md",
            repo_type="model",
        )

        with open(
            readmePath,
            "r",
            encoding="utf-8",
        ) as file:

            readme = file.read()


        # Prevent excessively large model cards from
        # being sent to the LLM.

        maxReadmeLength = 30000

        readme = readme[
            :maxReadmeLength
        ]


        evidence.append(
            {
                "source": "huggingface",

                "title": (
                    f"{repositoryId} Model Card"
                ),

                "url": modelUrl,

                "description": (
                    "Hugging Face model card / README."
                ),

                "metadata": {
                    "repositoryId": repositoryId,

                    "content": readme,
                },
            }
        )

    except Exception as error:

        print(
            "Failed to retrieve Hugging Face "
            f"model card for {repositoryId}:"
        )

        print(error)


    return evidence


# =====================================================
# MAIN DEPLOYABILITY CHECK
# =====================================================

def checkDeployability(
    candidate: dict,
    discoveryEvidence: list[dict],
    config: ResearchConfig,
) -> dict:
    """
    Determine whether the exact ASR model can be
    deployed locally.

    The process is:

    1. Start with Discovery evidence.
    2. Retrieve the exact Hugging Face repository.
    3. Ask the LLM to evaluate the evidence.
    4. If evidence is insufficient, perform targeted
       web searches.
    5. Re-evaluate the expanded evidence.
    6. Return True, False, or None.

    Local deployability requires evidence for BOTH:

    1. Downloadable model weights/checkpoint.
    2. A usable local inference path.
    """

    evidence = list(
        discoveryEvidence
    )

    # =================================================
    # 1. GET EXACT HF REPOSITORY EVIDENCE
    # =================================================

    huggingFaceEvidence = (
        getHuggingFaceEvidence(
            candidate
        )
    )

    evidence.extend(
        huggingFaceEvidence
    )

    evidence = deduplicateEvidence(
        evidence
    )


    # =================================================
    # 2. INITIAL LLM EVALUATION
    # =================================================

    searchCount = 0

    while True:

        decision = evaluateDeployability(
            candidate,
            evidence,
        )

        isLocallyDeployable = decision.get(
            "isLocallyDeployable"
        )

        # =================================================
        # ENOUGH INFORMATION
        # =================================================

        if isLocallyDeployable in (
            True,
            False,
        ):

            return {
                "isLocallyDeployable": (
                    isLocallyDeployable
                ),

                "reason": decision.get(
                    "reason"
                ),

                "evidence": evidence,
            }


        # =================================================
        # INSUFFICIENT INFORMATION
        # =================================================

        if searchCount >= (
            config.maxDeployabilitySearches
        ):

            return {
                "isLocallyDeployable": None,

                "reason": (
                    "Insufficient evidence to "
                    "determine local deployability "
                    "after targeted searches."
                ),

                "evidence": evidence,
            }


        nextQuery = decision.get(
            "nextQuery"
        )

        if not nextQuery:

            return {
                "isLocallyDeployable": None,

                "reason": (
                    "Insufficient evidence to "
                    "determine local deployability."
                ),

                "evidence": evidence,
            }


        # =================================================
        # TARGETED WEB SEARCH
        # =================================================

        searchCount += 1

        if config.verbose:

            print(
                "\nDeployability search "
                f"{searchCount}: {nextQuery}"
            )

        try:

            results = webSearch(
                nextQuery,
                maxResults=(
                    config.deployabilityResultsPerSearch
                ),
            )

            evidence.extend(
                results
            )

            evidence = deduplicateEvidence(
                evidence
            )

        except Exception as error:

            if config.verbose:

                print(
                    "Deployability search failed:"
                )

                print(error)

            # Continue to the next evaluation.
            # The LLM will decide whether the
            # existing evidence is sufficient.


# =====================================================
# LLM DEPLOYABILITY EVALUATION
# =====================================================

def evaluateDeployability(
    candidate: dict,
    evidence: list[dict],
) -> dict:
    """
    Use the LLM to evaluate whether the exact model
    can be deployed locally.

    The LLM may request ONE targeted search when the
    supplied evidence is insufficient.
    """

    response = llm.invoke(
        f"""
You are evaluating whether an automatic speech
recognition model can be deployed locally.

The candidate identity has already been established
during Discovery.

You must evaluate the EXACT model identified by the
repository ID.

Do not mix information from different model variants.

Candidate:

{json.dumps(
    candidate,
    indent=2,
    ensure_ascii=False,
)}

Evidence:

{json.dumps(
    evidence,
    indent=2,
    ensure_ascii=False,
)}


==================================================
REQUIREMENT 1 — MODEL WEIGHTS
==================================================

Determine whether actual model weights or checkpoints
for THIS EXACT MODEL are publicly downloadable.

Strong evidence includes:

- .safetensors
- .bin
- .pt
- .pth
- .ckpt
- .onnx
- checkpoint files
- explicit downloadable model weights
- documented loading of the exact repository

A model page existing on Hugging Face is NOT by itself
proof that usable weights are available.

Source code alone is NOT sufficient.

A paper alone is NOT sufficient.


==================================================
REQUIREMENT 2 — LOCAL INFERENCE PATH
==================================================

Determine whether THIS EXACT MODEL has a usable local
inference path.

Strong evidence includes:

- transformers.from_pretrained(...)
- Hugging Face Transformers loading instructions
- PyTorch inference
- ONNX Runtime
- official inference scripts
- local command-line inference
- documented local runtime
- explicit local execution instructions
- official repository instructions for running the model

Hosted APIs alone do NOT count.

A GitHub repository without a usable local inference
method does NOT count.


==================================================
DECISION RULE
==================================================

Return TRUE only when BOTH are supported:

1. Downloadable weights/checkpoint exist.

AND

2. A usable local inference path exists.


Return FALSE only when the evidence clearly establishes
that local deployment is not possible.

Examples:

- only a hosted API exists
- weights are unavailable
- repository explicitly requires a remote service
- model is only a paper
- model is only source code without weights


Return NULL when the evidence is insufficient to make
a reliable determination.

Do NOT guess.

Do NOT infer deployability merely because:

- the repository is public
- the model is on Hugging Face
- the repository contains Python code
- another model from the same family is deployable


==================================================
TARGETED SEARCH
==================================================

If the evidence is insufficient, generate ONE targeted
search query that specifically addresses the missing
deployability evidence.

Prioritize searches for:

- exact model repository
- exact model weights
- exact model inference instructions
- official GitHub repository
- official documentation
- local inference examples

Good examples:

"Qwen/Qwen3-ASR-0.6B local inference weights"

"Qwen/Qwen3-ASR-0.6B GitHub inference"

"exact-model-name transformers from_pretrained"

Do not generate a broad query.

Do not search for another model variant.

Return:

{{
    "isLocallyDeployable": null,
    "reason": "What evidence is still missing.",
    "nextQuery": "one targeted search query"
}}


==================================================
RETURN FORMAT
==================================================

If deployable:

{{
    "isLocallyDeployable": true,
    "reason": "Short evidence-based explanation.",
    "nextQuery": null
}}

If not deployable:

{{
    "isLocallyDeployable": false,
    "reason": "Short evidence-based explanation.",
    "nextQuery": null
}}

If insufficient evidence:

{{
    "isLocallyDeployable": null,
    "reason": "Short explanation of what is missing.",
    "nextQuery": "one targeted search query"
}}

Return ONLY valid JSON.
Do not include markdown.
Do not include code fences.
"""
    )


    # =================================================
    # PARSE LLM RESPONSE
    # =================================================

    try:

        result = json.loads(
            response.content
        )

        isLocallyDeployable = result.get(
            "isLocallyDeployable"
        )

        if isLocallyDeployable not in (
            True,
            False,
            None,
        ):

            isLocallyDeployable = None


        return {
            "isLocallyDeployable": (
                isLocallyDeployable
            ),

            "reason": result.get(
                "reason"
            ),

            "nextQuery": result.get(
                "nextQuery"
            ),
        }

    except (
        json.JSONDecodeError,
        TypeError,
    ):

        return {
            "isLocallyDeployable": None,

            "reason": (
                "The LLM returned an invalid "
                "deployability response."
            ),

            "nextQuery": None,
        }


# =====================================================
# EVIDENCE DEDUPLICATION
# =====================================================

def deduplicateEvidence(
    evidence: list[dict],
) -> list[dict]:
    """
    Remove duplicate evidence items using
    source + URL + title.
    """

    seen = set()

    unique = []

    for item in evidence:

        source = item.get(
            "source"
        )

        url = item.get(
            "url"
        )

        title = item.get(
            "title"
        )

        key = (
            source,
            url,
            title,
        )

        if key in seen:
            continue

        seen.add(
            key
        )

        unique.append(
            item
        )

    return unique