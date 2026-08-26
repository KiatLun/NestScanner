import json

from app.llm.client import getLLM

from app.models.schemas import (
    ModelProfile,
)

from app.tools.webSearch import (
    webSearch,
    deduplicateResults,
)

from app.tools.huggingFace import (
    searchHuggingFaceModels,
)

from app.tools.github import (
    searchGithubRepositories,
)

from app.tools.arvixSearch import (
    searchArxivPapers,
)


llm = getLLM()


def buildTechnicalProfile(
    candidate: dict,
    discoveryEvidence: list[dict],
    recencyEvidence: list[dict],
    deployabilityEvidence: list[dict],
    releaseDate: str | None,
) -> dict:
    """
    Gather deeper technical evidence and build the final
    model profile.

    This function should only be called after the model
    passes recency and local deployability checks.

    Returns:
    {
        "profile": dict,
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

    evidence = []

    evidence.extend(
        discoveryEvidence
    )

    evidence.extend(
        recencyEvidence
    )

    evidence.extend(
        deployabilityEvidence
    )

    # =================================================
    # 1. GATHER TECHNICAL EVIDENCE
    # =================================================

    queries = [
        f'"{modelName}" architecture',
        f'"{modelName}" parameter count',
        f'"{modelName}" languages',
        f'"{modelName}" WER benchmark',
        f'"{modelName}" fine tuning',
        f'"{modelName}" license',
    ]

    if organisation:
        queries.append(
            f'"{organisation}" "{modelName}" technical details'
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
                f"Technical web search failed: "
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
            "Technical Hugging Face search failed."
        )

        print(error)

    try:
        githubResults = searchGithubRepositories(
            modelName,
            limit=5,
        )

        evidence.extend(
            githubResults
        )

    except Exception as error:
        print(
            "Technical GitHub search failed."
        )

        print(error)

    try:
        arxivResults = searchArxivPapers(
            modelName,
            limit=5,
        )

        evidence.extend(
            arxivResults
        )

    except Exception as error:
        print(
            "Technical arXiv search failed."
        )

        print(error)

    evidence = deduplicateResults(
        evidence
    )

    # =================================================
    # 2. BUILD PROFILE
    # =================================================

    response = llm.invoke(f"""
You are building a technical profile for an automatic
speech recognition model.

Candidate:

{json.dumps(candidate, indent=2)}

Verified release date:

{releaseDate}

Research evidence:

{json.dumps(evidence, indent=2)}

Extract:

- name
- organisation
- releaseDate
- license
- architecture
- parameterCount
- languages
- reportedWer
- fineTuningSupport
- sourceUrls

Rules:

1. Use only supplied evidence.

2. Do not fabricate missing information.

3. If a scalar field cannot be established, use null.

4. If languages cannot be established, use [].

5. releaseDate MUST use the supplied release date:

{releaseDate}

6. For reportedWer:

   - include benchmark or dataset context when available
   - do not confuse CER with WER
   - do not convert CER into WER
   - if only CER is reported, use null

7. For fineTuningSupport:

   - state whether fine-tuning is supported
   - include relevant method/instructions when supported
   - use null if it cannot be established

8. Prefer official sources when evidence conflicts.

9. sourceUrls should contain the most useful sources
   supporting the technical profile.

Return ONLY valid JSON:

{{
    "name": "model name",
    "organisation": "organisation or null",
    "releaseDate": "{releaseDate}",
    "license": "license or null",
    "architecture": "architecture or null",
    "parameterCount": "parameter count or null",
    "languages": [],
    "reportedWer": "WER with context or null",
    "fineTuningSupport": "description or null",
    "sourceUrls": []
}}

Do not include markdown.
Do not include code fences.
Do not include explanations outside the JSON.
""")

    data = json.loads(
        response.content
    )

    validated = ModelProfile.model_validate(
        data
    )

    return {
        "profile": validated.model_dump(),
        "evidence": evidence,
    }