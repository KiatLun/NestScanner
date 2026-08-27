import json

from app.llm.client import getLLM

from app.models.schemas import (
    TechnicalProfile,
)

from app.agents.research.config import (
    ResearchConfig,
)

from app.tools.webSearch import (
    webSearch,
    deduplicateResults,
)

from app.tools.huggingFace import (
    searchHuggingFaceModels,
)

from app.tools.github import (
    searchGitHubRepositories,
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
    config: ResearchConfig,
) -> dict:
    """
    Gather deeper technical evidence and build the
    technical profile.

    This function should only be called after the model
    passes recency and local deployability checks.

    Returns:
    {
        "technicalProfile": dict,
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

    evidence.extend(discoveryEvidence)

    evidence.extend(recencyEvidence)

    evidence.extend(deployabilityEvidence)

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
        queries.append(f'"{organisation}" ' f'"{modelName}" technical details')

    # =================================================
    # WEB SEARCH
    # =================================================

    for query in queries:

        if config.verbose:
            print(f"\nTechnical web search: " f"{query}")

        try:
            results = webSearch(
                query,
                maxResults=(config.technicalResultsPerSearch),
            )

            evidence.extend(results)

        except Exception as error:

            if config.verbose:
                print("Technical web search " f"failed: {query}")

                print(error)

    # =================================================
    # HUGGING FACE
    # =================================================

    try:
        hfResults = searchHuggingFaceModels(
            modelName,
            limit=(config.technicalHuggingFaceResults),
        )

        evidence.extend(hfResults)

    except Exception as error:

        if config.verbose:
            print("Technical Hugging Face " "search failed.")

            print(error)

    # =================================================
    # GITHUB
    # =================================================

    try:
        githubResults = searchGitHubRepositories(
            modelName,
            limit=(config.technicalGithubResults),
        )

        evidence.extend(githubResults)

    except Exception as error:

        if config.verbose:
            print("Technical GitHub search " "failed.")

            print(error)

    # =================================================
    # ARXIV
    # =================================================

    try:
        arxivResults = searchArxivPapers(
            modelName,
            limit=(config.technicalArxivResults),
        )

        evidence.extend(arxivResults)

    except Exception as error:

        if config.verbose:
            print("Technical arXiv search " "failed.")

            print(error)

    # =================================================
    # DEDUPLICATE EVIDENCE
    # =================================================

    evidence = deduplicateResults(evidence)

    # =================================================
    # 2. BUILD TECHNICAL PROFILE
    # =================================================

    response = llm.invoke(f"""
You are building a technical profile for an automatic
speech recognition model.

The candidate identity has already been established
during Discovery.

Candidate context:

{json.dumps(candidate, indent=2)}

Verified release date:

{releaseDate}

Research evidence:

{json.dumps(evidence, indent=2)}

Extract ONLY the following technical information:

- license
- architecture
- parameterCount
- languages
- reportedWer
- fineTuningSupport

Do NOT return:

- name
- organisation
- sourceUrl
- candidateType
- releaseDate
- sourceUrls

Rules:

1. Use only the supplied evidence.

2. Do not fabricate or guess missing information.

3. If a scalar field cannot be established, use null.

4. If languages cannot be established, use [].

5. For architecture:

   - describe the model architecture only when clearly
     supported by the evidence
   - use null if the architecture cannot be established

6. For parameterCount:

   - use the parameter count for the exact candidate
     when possible
   - do not use the parameter count of another model
     variant unless the candidate represents the entire
     model family and the distinction is clearly stated
   - use null if it cannot be established

7. For languages:

   - include only languages or language coverage clearly
     supported by the evidence
   - do not infer language support

8. For reportedWer:

   - include benchmark or dataset context when available
   - do not confuse CER with WER
   - do not convert CER into WER
   - do not compare unrelated model variants
   - if only CER is reported, use null
   - use null if reliable WER cannot be established

9. For fineTuningSupport:

   - state whether fine-tuning is supported
   - include relevant method or instructions when
     supported
   - use null if it cannot be established

10. For license:

    - use the license associated with the actual model
      weights or repository when possible
    - do not infer a license from unrelated repositories
    - use null if it cannot be established

11. Prefer official sources when evidence conflicts.

12. Be strict about model identity. Do not mix technical
    details from different model variants unless the
    candidate represents a model family and the evidence
    clearly applies to the family.

Return ONLY valid JSON:

{{
    "license": "license or null",
    "architecture": "architecture or null",
    "parameterCount": "parameter count or null",
    "languages": [],
    "reportedWer": "WER with benchmark context or null",
    "fineTuningSupport": "description or null"
}}

Do not include markdown.
Do not include code fences.
Do not include explanations outside the JSON.
""")

    # =================================================
    # 3. VALIDATE PROFILE
    # =================================================

    data = json.loads(response.content)

    validated = TechnicalProfile.model_validate(data)

    return {
        "technicalProfile": (validated.model_dump()),
        "evidence": evidence,
    }
