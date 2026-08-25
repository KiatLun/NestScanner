import json

from app.llm.client import getLLM
from pydantic import BaseModel

llm = getLLM()


class DiscoverySearchPlan(BaseModel):
    webQueries: list[str]
    huggingFaceQueries: list[str]
    githubQueries: list[str]
    arxivQueries: list[str]


def buildDiscoveryQueries(
    objective: str,
) -> DiscoverySearchPlan:
    """
    Generate source-specific search queries.

    Different sources work better with different query styles.
    """

    response = llm.invoke(f"""
You are creating a search plan for an ASR technology scanner.

Objective:

{objective}

Generate concise source-specific search queries.

Important:

WEB SEARCH
- Can use natural language.
- Focus on recent releases and open-source ASR models.

HUGGING FACE
- Use short repository/model keywords.
- Do NOT use full natural-language questions.
- Examples:
  "ASR"
  "speech recognition"
  "multilingual ASR"

GITHUB
- Use short technical repository keywords.
- Do NOT use full natural-language questions.
- Examples:
  "automatic speech recognition"
  "ASR speech recognition"

ARXIV
- Use academic topic phrases.
- Examples:
  "automatic speech recognition"
  "multilingual speech recognition"

Return:

- up to 3 web queries
- up to 3 Hugging Face queries
- up to 3 GitHub queries
- up to 2 arXiv queries

Return ONLY valid JSON.

Use exactly this structure:

{{
  "webQueries": [],
  "huggingFaceQueries": [],
  "githubQueries": [],
  "arxivQueries": []
}}

Do not include markdown.
Do not include code fences.
Do not include explanations outside the JSON.
""")

    rawContent = response.content

    print("\n=== RAW SEARCH PLAN ===")
    print(rawContent)

    data = json.loads(rawContent)

    return DiscoverySearchPlan.model_validate(data)
