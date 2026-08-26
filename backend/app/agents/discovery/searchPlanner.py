import json

from pydantic import BaseModel, Field

from app.llm.client import getLLM


llm = getLLM()

USE_LLM_PLANNER = False


class DiscoverySearchPlan(BaseModel):
    webQueries: list[str] = Field(
        default_factory=list
    )

    huggingFaceQueries: list[str] = Field(
        default_factory=list
    )

    githubQueries: list[str] = Field(
        default_factory=list
    )

    arxivQueries: list[str] = Field(
        default_factory=list
    )


def buildDiscoveryQueries(
    objective: str,
) -> DiscoverySearchPlan:
    """
    Build source-specific search queries for Discovery.

    Set USE_LLM_PLANNER = False for deterministic
    hardcoded queries.

    Set USE_LLM_PLANNER = True to use the LLM planner.
    """

    if not USE_LLM_PLANNER:
        return buildHardcodedQueries()

    return buildLLMQueries(
        objective
    )


def buildHardcodedQueries() -> DiscoverySearchPlan:
    """
    Deterministic ASR discovery queries.
    """

    return DiscoverySearchPlan(
        webQueries=[
            "new automatic speech recognition model 2026",
            "new ASR model release 2026",
            "open source ASR model 2026",
            "new speech-to-text model 2026",
            "new transcription model announcement 2026",
            "multilingual ASR model release 2026",
            "streaming ASR model release 2026",
            "new open source speech recognition model 2026",
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
            "speech recognition model",
            "speech-to-text model",
            "transcription model",
            "multilingual ASR model",
            "streaming ASR model",
            "ASR pretrained",
        ],
        arxivQueries=[
            "automatic speech recognition",
            "end-to-end speech recognition",
            "multilingual speech recognition",
            "streaming automatic speech recognition",
            "speech recognition model",
            "speech-to-text model",
            "ASR foundation model",
            "large speech recognition model",
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

Your goal is to discover identifiable ASR models or
model families from recent sources.

Discovery is only responsible for scouting candidate
models.

Discovery does NOT verify:

- exact release date
- whether the model is truly recent
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

Use short keyword-oriented queries.

Prefer approximately 1 to 4 words.

Good styles:

"ASR"
"speech recognition"
"automatic speech recognition"
"speech-to-text"
"transcription"
"multilingual ASR"
"streaming ASR"
"pretrained ASR"

Avoid long natural-language queries.

Generate approximately 5 to 8 queries.


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

Generate approximately 5 to 8 queries.


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

Generate approximately 5 to 8 queries.


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

    data = json.loads(
        response.content
    )

    return DiscoverySearchPlan.model_validate(
        data
    )