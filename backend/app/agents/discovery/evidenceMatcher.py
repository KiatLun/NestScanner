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

1. Group evidence that refers to the SAME underlying
   automatic speech recognition model or model family.

2. Return ONLY groups that represent an identifiable
   automatic speech recognition model or model family
   worth passing to the Research Agent.

Evidence may come from:

- general web search
- Hugging Face
- GitHub
- arXiv

Different sources may describe the same model using
different names.

========================================================
VALID DISCOVERY CANDIDATE
========================================================

A returned candidate MUST:

1. Be an automatic speech recognition model or
   model family.

2. Have a clear and identifiable model/model-family
   identity.

3. Have supporting evidence in the supplied data.

4. Be something that can reasonably be passed to
   Research for deeper investigation.

Do NOT return evidence groups for:

- tutorials
- generic articles
- surveys
- leaderboards
- software libraries
- ASR toolkits
- benchmark pages
- unrelated speech systems
- APIs without an identifiable underlying model
- papers that do not correspond to an identifiable
  model or model family

If evidence discusses ASR generally but does not identify
a specific model/model family, omit it.

========================================================
GROUPING RULES
========================================================

1. Only group evidence when it clearly refers to the
   SAME underlying model or model family.

2. Being produced by the same organisation is NOT enough.

For example:

Organisation X / Model A

and:

Organisation X / Model B

must remain separate.

3. Different parameter-size checkpoints MAY be grouped
   when they clearly belong to the same model family.

For example:

Qwen3-ASR-0.6B

and:

Qwen3-ASR-1.7B

may be grouped as:

Qwen3-ASR

4. Do NOT automatically merge a separately named
   derived model with its base model.

This includes:

- fine-tuned models
- adapted models
- distilled models
- quantized models
- converted models
- language-specific models
- domain-specific models

For example:

ASLP-lab/CN-MultiDialect-ASR

must NOT automatically be grouped with:

Qwen/Qwen3-ASR

even if metadata contains:

base_model:Qwen/Qwen3-ASR

or:

base_model:finetune:Qwen/Qwen3-ASR

These fields indicate a relationship.

They do NOT mean both items are the same model release.

5. If it is uncertain whether two items refer to the
   same model, keep them separate.

Prefer separate candidates over incorrectly merging
different models.

========================================================
CANDIDATE INFORMATION
========================================================

For each candidate:

name:
- Use the actual model/model-family name.
- Do not use the title of an article as the model name.

organisation:
- Use the organisation responsible for the model when
  supported by evidence.
- Otherwise use null.

sourceUrl:
Choose the most useful supplied source for identifying
the model.

Prefer:

1. Hugging Face model page
2. official project page
3. official GitHub repository
4. official research page
5. arXiv paper
6. credible announcement/article

reason:
- Give a short reason explaining why this is an
  identifiable ASR model/model family.
- Do NOT perform deep technical analysis.

candidateType must be one of:

- "model"
- "model_family"
- "toolkit"
- "paper_only"
- "unknown"

Returned candidates should normally be:

- "model"
- "model_family"

Do not return toolkit or paper_only items unless they
also correspond to an identifiable model/model family.

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

Only include evidence that actually supports the
candidate's identity.

========================================================
DISCOVERY SCOPE
========================================================

Discovery does NOT verify:

- true model release date
- whether the model satisfies the recency requirement
- licensing
- model weights
- local deployability
- architecture
- parameter count
- WER or CER
- benchmarks
- fine-tuning support
- hardware requirements

Those belong to the Research Agent.

Do NOT reject a candidate simply because its true
release date has not yet been established.

========================================================
OUTPUT
========================================================

Return ONLY valid JSON.

Use exactly this structure:

{{
    "candidates": [
        {{
            "candidate": {{
                "name": "model name",
                "organisation": "organisation or null",
                "sourceUrl": "primary source URL or null",
                "reason": "short reason this is an ASR model",
                "candidateType": "model"
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

    candidates = candidates[: config.maxCandidates]

    if config.verbose:
        print(f"\nCreated " f"{len(candidates)} " "Discovery candidates.")

    return candidates
