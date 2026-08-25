import json

from app.llm.client import getLLM
from app.models.schemas import EvidenceGroup

llm = getLLM()


def groupModelEvidence(
    results: list[dict],
) -> list[dict]:
    """
    Use the LLM to group discovery results that refer
    to the same ASR model or model family.

    Separately released derived models should remain
    separate from their base models.
    """

    if not results:
        return []

    response = llm.invoke(f"""
You are performing entity matching for an ASR technology scanner.

Below are discovery results collected from multiple sources:

- general web
- Hugging Face
- GitHub
- arXiv

Results:

{json.dumps(results, indent=2)}

Your job is to group evidence that refers to the SAME
ASR model or model family.

Examples of evidence that may belong to the same group:

- a Hugging Face model repository
- an official GitHub repository
- an arXiv paper
- an official project page
- an official announcement

Rules:

1. Only group results when there is reasonable evidence that
   they refer to the same underlying model or model family.

2. Do NOT group items simply because they come from the
   same organisation.

3. Do NOT merge distinct model families.

4. Different parameter-size checkpoints of the SAME model
   family may be grouped.

For example:

- Qwen3-ASR-0.6B
- Qwen3-ASR-1.7B

may be grouped as:

Qwen3-ASR

if the supplied evidence indicates that they are variants
of the same model family.

5. A separately named derived model must NOT automatically
   be grouped with its base model.

This includes:

- fine-tuned models
- adapted models
- distilled models
- quantized models
- converted models
- domain-specific derivatives
- language-specific derivatives

For example:

ASLP-lab/CN-MultiDialect-ASR

with metadata such as:

base_model:Qwen/Qwen3-ASR-1.7B

or:

base_model:finetune:Qwen/Qwen3-ASR-1.7B

is NOT the same model as Qwen3-ASR.

It is a separate released model that happens to use
Qwen3-ASR as its base model.

6. Treat metadata beginning with:

base_model:

or:

base_model:finetune:

as a relationship between models, NOT proof that they
are the same model.

7. Similarly, a separately named quantized or derived model,
such as:

VibeVoice-ASR-BitNet

should remain separate from:

VibeVoice-ASR

if the evidence indicates that it is a separately released
derived model rather than merely another parameter-size
checkpoint of the same release.

8. If uncertain whether two results represent the same model,
keep them separate.

It is better to create two groups than to incorrectly merge
two different model releases.

9. Preserve the supplied URLs and evidence exactly.

10. Do not invent evidence.

11. modelName should be the clearest canonical model or
model-family name supported by the evidence.

12. organisation should be null if it cannot be determined
from the supplied evidence.

13. Do NOT create standalone model groups for items that
are clearly only:

- leaderboards
- tutorials
- surveys
- generic articles
- software libraries
- comparison pages

These may only be included as supporting evidence for an
identifiable model if they clearly refer to that model.

14. A paper should only form or support a model group when
it describes an identifiable ASR model or model family.

Return ONLY valid JSON.

Use exactly this structure:

{{
  "groups": [
    {{
      "modelName": "model name",
      "organisation": "organisation or null",
      "evidence": [
        {{
          "source": "source",
          "title": "original title",
          "url": "original URL",
          "description": "description or null",
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

    print("\n=== EVIDENCE MATCHING RESPONSE ===")
    print(rawContent)

    data = json.loads(rawContent)

    groups = []

    for group in data.get(
        "groups",
        [],
    ):
        validated = EvidenceGroup.model_validate(group)

        groups.append(validated.model_dump())

    return groups
