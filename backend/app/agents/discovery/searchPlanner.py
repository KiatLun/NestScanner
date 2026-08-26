import json

from pydantic import BaseModel, Field

from app.llm.client import getLLM


llm = getLLM()


class DiscoverySearchPlan(BaseModel):
    webQueries: list[str] = Field(default_factory=list)
    huggingFaceQueries: list[str] = Field(default_factory=list)
    githubQueries: list[str] = Field(default_factory=list)
    arxivQueries: list[str] = Field(default_factory=list)


def buildDiscoveryQueries(
    objective: str,
) -> DiscoverySearchPlan:
    """
    Build source-specific search queries for Discovery.
    """

    response = llm.invoke(f"""
You are the search planner for an automatic speech
recognition technology discovery agent.

Objective:

{objective}

Generate targeted search queries for four sources:

1. General web search
2. Hugging Face
3. GitHub
4. arXiv

The purpose of Discovery is to scout likely ASR models
or model families appearing in recent sources.

Discovery does NOT need to establish the true model
release date.

That will be verified later by the Research Agent.

Search for evidence such as:

- ASR model announcements
- new speech recognition models
- model repositories
- research projects
- model families
- automatic speech recognition releases
- speech-to-text models

Avoid queries focused on:

- licensing
- hardware requirements
- WER analysis
- fine-tuning
- deployment
- architecture details
- parameter counts

Those belong to Research.

Keep the queries concise and useful for each source.

Generate approximately:

- 2 to 4 web queries
- 1 to 3 Hugging Face queries
- 1 to 3 GitHub queries
- 1 to 3 arXiv queries

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