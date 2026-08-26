import json

from app.llm.client import getLLM

from app.tools.webSearch import (
    webSearch,
    deduplicateResults,
)

from app.tools.huggingFace import (
    searchHuggingFaceModels,
)


llm = getLLM()


def checkRecency(
    candidate: dict,
    discoveryEvidence: list[dict],
    days: int = 30,
) -> dict:
    """
    Gather release-related evidence and determine whether
    the model was released within the past `days` days.

    Returns:
    {
        "releaseDate": str | None,
        "isRecent": bool,
        "evidence": list[dict]
    }
    """

    modelName = candidate.get(
        "name",
        "",
    )

    organisation = candidate.get(
        "organisation",
        "",
    )

    evidence = list(
        discoveryEvidence
    )

    # =================================================
    # 1. GATHER RELEASE EVIDENCE
    # =================================================

    queries = [
        f'"{modelName}" release',
        f'"{modelName}" released',
        f'"{modelName}" announcement',
    ]

    if organisation:
        queries.append(
            f'"{organisation}" "{modelName}" release'
        )

    for query in queries:
        try:
            results = webSearch(
                query,
                maxResults=5,
            )

            evidence.extend(
                results
            )

        except Exception as error:
            print(
                f"Recency web search failed: "
                f"{query}"
            )

            print(error)

    try:
        hfResults = searchHuggingFaceModels(
            modelName,
            limit=10,
        )

        evidence.extend(
            hfResults
        )

    except Exception as error:
        print(
            "Recency Hugging Face search failed."
        )

        print(error)

    evidence = deduplicateResults(
        evidence
    )

    # =================================================
    # 2. CHECK RECENCY USING LLM
    # =================================================

    response = llm.invoke(f"""
You are checking whether an automatic speech recognition
model was actually released within the past {days} days.

Candidate:

{json.dumps(candidate, indent=2)}

Evidence:

{json.dumps(evidence, indent=2)}

Your tasks:

1. Determine the actual release date of THIS model or
   model family.

2. Decide whether that release date falls within the
   past {days} days.

Important rules:

1. Use only supplied evidence.

2. Prefer explicit release statements such as:

   - "released on ..."
   - "we release ..."
   - "launched on ..."
   - "announced on ..."
   - "available today ..."

3. Prefer authoritative sources such as:

   - official organisation announcements
   - official project pages
   - official Hugging Face repositories
   - official GitHub repositories
   - official research/project pages

4. Do NOT treat these as release dates unless explicitly
   tied to the model's release:

   - article publication date
   - repository update date
   - model-card modification date
   - page retrieval date
   - benchmark date

5. Do not use dates belonging to another model.

6. A recent article discussing an older model does NOT
   make the model recent.

7. If the actual release date cannot be established,
   return releaseDate=null and isRecent=false.

Return ONLY valid JSON:

{{
    "releaseDate": "YYYY-MM-DD or null",
    "isRecent": true
}}

Do not include markdown.
Do not include code fences.
Do not include explanations outside the JSON.
""")

    try:
        result = json.loads(
            response.content
        )

    except json.JSONDecodeError:
        result = {
            "releaseDate": None,
            "isRecent": False,
        }

    return {
        "releaseDate": result.get(
            "releaseDate"
        ),
        "isRecent": result.get(
            "isRecent",
            False,
        ),
        "evidence": evidence,
    }