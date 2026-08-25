import json

from app.llm.client import getLLM
from app.models.schemas import EvidenceGroup


llm = getLLM()


def groupModelEvidence(
    searchResults: list[dict],
) -> list[dict]:
    """
    Group discovery evidence that refers to the same
    ASR model or model family.

    Uses the LLM because cross-source naming can differ
    significantly across web, Hugging Face, GitHub,
    and arXiv.
    """

    if not searchResults:
        return []

    response = llm.invoke(f"""
You are performing cross-source evidence matching for an
ASR technology scanner.

Discovery evidence:

{json.dumps(searchResults, indent=2)}

Your task is to group evidence that clearly refers to the
SAME automatic speech recognition model or model family.

Different sources may describe the same model differently.

For example:

- a Hugging Face repository
- an official GitHub repository
- an arXiv paper
- an official announcement
- a web article

may all refer to the same underlying model.

Your goal is to connect those pieces of evidence.

========================================================
GROUPING RULES
========================================================

1. Only group evidence when it refers to the same
   underlying model or model family.

2. Being produced by the same organisation is NOT enough.

For example:

Organisation X / Model A

and

Organisation X / Model B

must remain separate.

3. Different parameter-size checkpoints MAY be grouped
   when they clearly belong to the same model family.

For example:

Qwen3-ASR-0.6B

and

Qwen3-ASR-1.7B

may be grouped as:

Qwen3-ASR

4. Do NOT automatically group a fine-tuned model with
   its base model.

A separately named:

- fine-tuned model
- adapted model
- distilled model
- quantized model
- converted model
- language-specific model
- domain-specific model
- derivative model

should remain separate when it has its own model identity.

For example:

ASLP-lab/CN-MultiDialect-ASR

must NOT automatically be grouped with:

Qwen/Qwen3-ASR

even if its metadata contains:

base_model:Qwen/Qwen3-ASR

or:

base_model:finetune:Qwen/Qwen3-ASR

Those fields indicate a RELATIONSHIP between models,
not that they are the same model release.

5. A base-model relationship does NOT mean two models
   belong in the same evidence group.

6. If two items have similar names but it is unclear
   whether they are the same model, keep them separate.

When uncertain, prefer separate groups rather than
incorrectly merging evidence.

7. Do not create standalone model groups for evidence
   that is only:

- a leaderboard
- a tutorial
- a survey
- a generic article
- a software library
- a general ASR toolkit
- a benchmark page

unless that evidence clearly supports an identifiable
ASR model or model family.

8. A research paper may support a model group when the
   paper clearly introduces or describes that model.

9. Preserve the supplied evidence.

Do not invent URLs, titles, organisations, model names,
metadata, or descriptions.

10. Choose a useful canonical modelName for each group.

Prefer the actual model/model-family name rather than
the title of an article discussing it.

11. organisation should refer to the organisation or
research group responsible for that model when this can
be determined from the supplied evidence.

If it cannot be determined, use null.

========================================================
OUTPUT FORMAT
========================================================

Return ONLY valid JSON.

Use camelCase field names.

Use exactly this structure:

{{
    "groups": [
        {{
            "modelName": "model or model family name",
            "organisation": "organisation or null",
            "evidence": [
                {{
                    "source": "source name",
                    "title": "original evidence title",
                    "url": "original URL",
                    "description": "original description or null",
                    "metadata": {{}}
                }}
            ]
        }}
    ]
}}

Do not include markdown.

Do not include code fences.

Do not include explanations outside the JSON.
""")

    rawContent = response.content

    print(
        "\n=== RAW EVIDENCE MATCHER RESPONSE ==="
    )

    print(
        rawContent
    )

    data = json.loads(
        rawContent
    )

    evidenceGroups = []

    for groupData in data.get(
        "groups",
        [],
    ):

        validatedGroup = (
            EvidenceGroup.model_validate(
                groupData
            )
        )

        evidenceGroups.append(
            validatedGroup.model_dump()
        )

    return evidenceGroups