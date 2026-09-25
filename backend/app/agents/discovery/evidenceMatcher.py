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

2. Represent one specific identifiable model or checkpoint.

3. Have an exact Hugging Face repositoryId.

4. Have supporting evidence in the supplied data.

5. Be suitable for deeper investigation by the Research Agent.

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

Each candidate represents ONE specific Hugging Face model
repository.

The Hugging Face repositoryId is the unique identity of a
model.

Different Hugging Face repositories MUST be treated as
different models.

For example:

Qwen/Qwen3-ASR-0.6B

and:

Qwen/Qwen3-ASR-1.7B

are two separate models because they have different
repository IDs.

Return them as two separate candidates.

Do NOT combine them into:

Qwen3-ASR

Do NOT create model families.

The same applies to:

- Base vs Large variants
- Small vs Large variants
- different parameter sizes
- different checkpoints
- language-specific variants
- domain-specific variants
- fine-tuned models
- distilled models
- quantized models
- adapted models

if they have their own Hugging Face repositoryId.

Only group evidence when all evidence refers to the exact
same Hugging Face repositoryId.

The organisation name is NOT a model identity.

For example:

Organisation:
Qwen

Repository:
Qwen/Qwen3-ASR-0.6B

and:

Repository:
Qwen/Qwen3-ASR-1.7B

must remain separate.

If two evidence items cannot be confidently matched to the
same repositoryId, keep them as separate candidates.

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
MODEL IDENTITY
========================================================

Every returned candidate MUST have an exact Hugging Face
repository identifier.

The repositoryId is the unique identity of the model.

If evidence does not contain a Hugging Face repository ID,
omit this candidate.

Do NOT create candidates from only:
- articles
- papers
- GitHub repositories
- organisation names

unless the exact Hugging Face repository can also be
identified.

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
                "repositoryId": "Hugging Face repository ID",
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
    print("RAW CONTENT TYPE:", type(rawContent))
    print("RAW CONTENT LENGTH:", len(rawContent))
    print("RAW CONTENT:", repr(rawContent))
    if config.verbose:
        print("\n=== RAW EVIDENCE MATCHER RESPONSE ===")

        print(rawContent)

    data = json.loads(rawContent)

    validated = DiscoveryCandidateList.model_validate(data)

    candidates = [candidate.model_dump() for candidate in validated.candidates]


    if config.verbose:
        print(f"\nCreated " f"{len(candidates)} " "Discovery candidates.")

    return candidates
