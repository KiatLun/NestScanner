import json

from app.llm.client import getLLM

from app.models.schemas import (
    DiscoveryCandidateList,
)

from app.agents.discovery.config import (
    DiscoveryConfig,
)

llm = getLLM()


def groupModelEvidence(
    searchResults: list[dict],
    config: DiscoveryConfig,
) -> list[dict]:
    """
    Group cross-source evidence by ASR model/model family
    and return only valid Discovery candidates.

    Each returned candidate includes the discovery evidence
    that supports its identity.
    """

    if not searchResults:
        return []

    if config.verbose:
        print("\n=== CROSS-SOURCE EVIDENCE MATCHING ===")

    response = llm.invoke(f"""
You are performing cross-source evidence matching for an
ASR technology discovery agent.

Discovery evidence:

{json.dumps(searchResults, indent=2)}

Your task has TWO responsibilities:

1. Identify each distinct automatic speech recognition
   model represented in the evidence.

2. Group evidence only when it refers to the EXACT SAME
   model or published checkpoint.

Evidence may come from:

- Hugging Face
- general web search
- GitHub
- arXiv

Hugging Face should be treated as the preferred source
for model identity.

========================================================
VALID DISCOVERY CANDIDATE
========================================================

A returned candidate MUST:

1. Be an automatic speech recognition model.

2. Represent one specific identifiable model or
   checkpoint.

3. Have supporting evidence in the supplied data.

4. Be suitable for deeper investigation by the Research
   Agent.

Do NOT return:

- tutorials
- generic articles
- surveys
- leaderboards
- software libraries
- ASR toolkits
- benchmark pages
- unrelated speech systems
- APIs without an identifiable underlying model
- papers that do not correspond to an identifiable model

========================================================
MODEL IDENTITY RULES
========================================================

Each candidate represents ONE specific model.

Different parameter-size variants are DIFFERENT models.

For example:

Qwen3-ASR-0.6B

and:

Qwen3-ASR-1.7B

MUST be returned as two separate candidates.

Do NOT combine them under:

Qwen3-ASR

The same applies to variants such as:

Model-Base
Model-Large

when they are separately published checkpoints.

Fine-tuned models, distilled models, quantized models,
language-specific models, domain-specific models, and
adapted models should also remain separate when they have
their own identifiable model repository or model name.

Only group evidence when it refers to the exact same
model/checkpoint.

Being produced by the same organisation is NOT enough.

If uncertain whether two results represent the exact
same model, keep them separate.

========================================================
MODEL NAME
========================================================

Use the official published model name.

When Hugging Face evidence exists, derive the name from
the Hugging Face repository identifier.

Example:

Hugging Face repository:

Qwen/Qwen3-ASR-0.6B

Return:

name:
Qwen3-ASR-0.6B

organisation:
Qwen

repositoryId:
Qwen/Qwen3-ASR-0.6B

sourceUrl:
the Hugging Face model URL

Do NOT remove or generalize:

- parameter sizes
- version numbers
- checkpoint names
- language identifiers
- variant identifiers
- Base / Large / Small identifiers

Do not invent a cleaner or more general model name.

========================================================
MODEL ID
========================================================

If Hugging Face evidence exists, modelId MUST be the exact
Hugging Face repository identifier.

Example:

Qwen/Qwen3-ASR-0.6B

Preserve it exactly.

Do not normalize, shorten, or rewrite it.

If there is no Hugging Face repository available,
modelId may be null.

========================================================
ORGANISATION
========================================================

Use the organisation responsible for the model when
supported by evidence.

For Hugging Face, the repository namespace may be used
when appropriate.

Otherwise return null.

========================================================
SOURCE URL
========================================================

Choose the most useful supplied source.

Prefer:

1. Hugging Face model page
2. official project page
3. official GitHub repository
4. official research page
5. arXiv paper
6. credible article

========================================================
DISCOVERY EVIDENCE
========================================================

For discoveryEvidence:

- copy relevant evidence directly from the supplied data
- preserve source
- preserve title
- preserve URL
- preserve description
- preserve metadata
- do not invent evidence
- do not rewrite evidence into new claims

Only include evidence supporting that exact model.

========================================================
OUTPUT
========================================================

Return ONLY valid JSON.

Use exactly this structure:

{{
    "candidates": [
        {{
            "candidate": {{
                "name": "official model name",
                "organisation": "organisation or null",
                "repositoryId": "Hugging Face repository ID or null",
                "sourceUrl": "primary source URL or null"
            }},
            "discoveryEvidence": [
                {{
                    "source": "source",
                    "title": "original title",
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

    if config.verbose:
        print("\n=== RAW EVIDENCE MATCHER RESPONSE ===")

        print(rawContent)

    data = json.loads(rawContent)

    validated = DiscoveryCandidateList.model_validate(data)

    candidates = [candidate.model_dump() for candidate in validated.candidates]


    if config.verbose:
        print(f"\nCreated " f"{len(candidates)} " "Discovery candidates.")

    return candidates
