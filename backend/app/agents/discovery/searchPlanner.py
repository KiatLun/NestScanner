import json

from pydantic import BaseModel, Field

from app.llm.client import getLLM

from app.agents.discovery.config import (
    DiscoveryConfig,
)

llm = getLLM()


class DiscoverySearchPlan(BaseModel):
    webQueries: list[str] = Field(default_factory=list)

    huggingFaceQueries: list[str] = Field(default_factory=list)

    githubQueries: list[str] = Field(default_factory=list)

    arxivQueries: list[str] = Field(default_factory=list)


def buildDiscoveryQueries(
    objective: str,
    config: DiscoveryConfig,
) -> DiscoverySearchPlan:
    """
    Build source-specific search queries for Discovery.

    Planner mode is controlled through DiscoveryConfig.
    """

    if not config.useLlmPlanner:
        return buildHardcodedQueries()

    return buildLLMQueries(objective)


def buildHardcodedQueries() -> DiscoverySearchPlan:
    """
    Deterministic ASR discovery queries.
    Hugging Face is the primary discovery source.
    """

    return DiscoverySearchPlan(
        webQueries=[
            "automatic speech recognition model",
            "open source ASR model",
            "speech-to-text model",
            "transcription model",
            "multilingual ASR model",
            "streaming ASR model",
        ],

        huggingFaceQueries=[
            "ASR",
            "automatic speech recognition",
            "speech recognition",
            "speech-to-text",
            "transcription",
            "multilingual ASR",
            "streaming ASR",
            "pretrained ASR",
        ],

        githubQueries=[
            "ASR model",
            "automatic speech recognition model",
            "speech-to-text model",
            "transcription model",
            "multilingual ASR model",
            "streaming ASR model",
        ],

        arxivQueries=[
            "automatic speech recognition",
            "end-to-end speech recognition",
            "multilingual speech recognition",
            "streaming automatic speech recognition",
            "speech recognition model",
            "speech-to-text model",
        ],
    )


def buildLLMQueries(
    objective: str,
) -> DiscoverySearchPlan:
    """
    Use the LLM to dynamically generate source-specific
    ASR discovery queries.
    """

    response = llm.invoke(f"""
You are the search planner for an automatic speech
recognition technology discovery agent.

Objective:

{objective}

Your goal is to discover identifiable automatic speech
recognition models.

Hugging Face is the PRIMARY discovery source.

The agent should discover specific published models or
checkpoints, not model families.

Different model variants must be treated as different
models.

Examples:

Qwen3-ASR-0.6B

and:

Qwen3-ASR-1.7B

are two different models.

Do not collapse them into a shared model family.

Discovery is only responsible for identifying candidate
models.

Discovery does NOT verify:

- license
- local deployability
- hardware requirements
- architecture
- parameter count
- WER
- fine-tuning support

Those responsibilities belong to the Research Agent.


GENERAL STRATEGY

Generate diverse source-specific search queries.

Focus on:

- automatic speech recognition
- ASR
- speech recognition
- speech-to-text
- transcription
- multilingual ASR
- streaming ASR
- real-time transcription
- open-source ASR
- pretrained ASR
- foundation speech models
- end-to-end ASR
- large speech recognition models
- model releases
- model repositories


WEB SEARCH

Use natural-language queries likely to surface:

- official announcements
- release posts
- research project pages
- model repositories
- technology news
- recent ASR model roundups

Generate approximately 5 to 8 queries.


HUGGING FACE SEARCH

Hugging Face is the primary model discovery source.

Use short keyword-oriented queries that are likely to
surface actual model repositories.

Prefer approximately 1 to 4 words.

Examples:

"ASR"
"speech recognition"
"automatic speech recognition"
"speech-to-text"
"transcription"
"multilingual ASR"
"streaming ASR"
"pretrained ASR"

Avoid long natural-language queries.

Generate approximately 6 to 10 queries.


GITHUB SEARCH

Use repository-style search terms.

Good styles:

"ASR model"
"automatic speech recognition model"
"speech recognition model"
"speech-to-text model"
"transcription model"
"multilingual ASR model"
"streaming ASR model"
"ASR pretrained"

Avoid conversational sentences.

Generate approximately 4 to 5 queries.


ARXIV SEARCH

Use academic ASR terminology.

Good styles:

"automatic speech recognition"
"end-to-end speech recognition"
"multilingual speech recognition"
"streaming automatic speech recognition"
"speech recognition model"
"speech-to-text model"
"ASR foundation model"
"large speech recognition model"

Generate approximately 2 to 5 queries.


QUERY DIVERSITY

Do not generate many near-duplicate queries.

Optimize each query for its specific source.

Do not use specific model names unless the objective
already mentions them.


Return ONLY valid JSON:

{{
    "webQueries": [
        "query"
    ],
    "huggingFaceQueries": [
        "query"
    ],
    "githubQueries": [
        "query"
    ],
    "arxivQueries": [
        "query"
    ]
}}

Do not include markdown.
Do not include code fences.
Do not include explanations outside the JSON.
""")

    data = json.loads(response.content)

    return DiscoverySearchPlan.model_validate(data)
