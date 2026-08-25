import json

from datetime import (
    date,
    timedelta,
    datetime,
)

from zoneinfo import ZoneInfo

from app.llm.client import getLLM

from app.models.schemas import (
    CandidateList,
    DiscoveryDecision,
)

from app.models.state import ScanState

from app.helper.searchPlanner import (
    buildDiscoveryQueries,
)

from app.helper.getModelReleaseData import (
    getModelReleaseDate,
)

from app.helper.checkRecency import (
    checkRecency,
)

from app.tools.webSearch import (
    webSearch,
    deduplicateResults,
)

from app.tools.huggingFace import (
    searchHuggingFaceModels,
    filterASRModels,
)

from app.tools.github import (
    searchGithubRepositories,
)

from app.tools.arvixSearch import (
    searchArxivPapers,
)

from app.helper.evidenceMatcher import (
    groupModelEvidence,
)


llm = getLLM()


# =====================================================
# DATE WINDOW
# =====================================================


def getDiscoveryDateWindow() -> tuple[date, date]:
    """
    Return the strict 30-day discovery window
    using Singapore local time.
    """

    currentDate = datetime.now(
        ZoneInfo("Asia/Singapore")
    ).date()

    cutoffDate = (
        currentDate
        - timedelta(days=30)
    )

    return cutoffDate, currentDate


# =====================================================
# SEARCH COVERAGE EVALUATION
# =====================================================


def evaluateSearchResults(
    objective: str,
    searchResults: list[dict],
    cutoffDate: date,
    currentDate: date,
) -> DiscoveryDecision:
    """
    Check whether the current search results contain
    enough recent ASR candidates.

    If not, request one additional targeted web search.
    """

    response = llm.invoke(f"""
You are evaluating search coverage for an ASR technology scanner.

Objective:

{objective}

Current date:

{currentDate}

Strict model release window:

{cutoffDate} to {currentDate}

Current discovery evidence:

{json.dumps(searchResults, indent=2)}

Discovery has exactly two responsibilities:

1. Find models or model families released within the
   specified 30-day release window.

2. Ensure that they are actually automatic speech
   recognition models.

Your job here is ONLY to determine whether the current
search results provide enough coverage to identify several
such candidates.

Check:

1. Are several actual ASR models or model families represented?
2. Are model releases from {cutoffDate} to {currentDate}
   represented?
3. Are there multiple distinct candidate models?
4. Are the results mostly relevant to automatic speech recognition?
5. Are the results dominated by irrelevant items such as:
   - tutorials
   - surveys
   - software libraries
   - generic articles
   - unrelated speech systems
6. Is there enough evidence to identify recent ASR candidates
   confidently and pass them to the Research Agent?

Important:

- Use the exact release window above.
- Do NOT invent a different current date.
- Do NOT search for releases outside the specified date range.
- A recently updated old model does NOT count as a recent release.
- A recent article mentioning an old model does NOT make the
  model recent.

Do NOT investigate:

- public model weights
- source-code availability
- local deployability
- licensing
- architecture
- benchmarks
- fine-tuning
- hardware requirements

Those belong to the Research Agent.

If the results are sufficient, return:

{{
  "enoughInformation": true,
  "nextQuery": null
}}

If additional discovery is required, return:

{{
  "enoughInformation": false,
  "nextQuery": "one additional useful web search query"
}}

If proposing another search query:

- explicitly target ASR model releases between
  {cutoffDate} and {currentDate}
- do not use dates outside this range

Return ONLY valid JSON.

Do not include markdown.
Do not include code fences.
Do not include explanations outside the JSON.
""")

    rawContent = response.content

    print(
        "\n=== SEARCH COVERAGE DECISION ==="
    )

    print(
        rawContent
    )

    data = json.loads(
        rawContent
    )

    return (
        DiscoveryDecision.model_validate(
            data
        )
    )


# =====================================================
# DISCOVERY AGENT
# =====================================================


def discoveryAgent(
    state: ScanState,
) -> dict:
    """
    Discover recent ASR model candidates.

    Discovery is responsible only for:

    1. Finding models/model families released
       within the past 30 days.

    2. Checking that they are actually ASR.

    Everything else belongs to Research.
    """

    print(
        "\n"
        + "=" * 60
    )

    print(
        "DISCOVERY AGENT"
    )

    print(
        "=" * 60
    )

    objective = (
        state["query"]
    )

    cutoffDate, currentDate = (
        getDiscoveryDateWindow()
    )

    print(
        f"\nObjective:\n{objective}"
    )

    print(
        f"\nStrict release window: "
        f"{cutoffDate} to {currentDate}"
    )

    # =================================================
    # 1. BUILD SOURCE-SPECIFIC SEARCH PLAN
    # =================================================

    searchObjective = f"""
{objective}

Current date: {currentDate}

Only discover ASR models or model families released
between {cutoffDate} and {currentDate}.

This is a strict 30-day model-release window.

Do not treat recent repository updates, model-card edits,
or articles about older models as new model releases.
"""

    searchPlan = (
        buildDiscoveryQueries(
            searchObjective
        )
    )

    print(
        "\n=== SEARCH PLAN ==="
    )

    print(
        "\nWeb queries:"
    )

    for query in (
        searchPlan.webQueries
    ):

        print(
            f"- {query}"
        )

    print(
        "\nHugging Face queries:"
    )

    for query in (
        searchPlan.huggingFaceQueries
    ):

        print(
            f"- {query}"
        )

    print(
        "\nGitHub queries:"
    )

    for query in (
        searchPlan.githubQueries
    ):

        print(
            f"- {query}"
        )

    print(
        "\narXiv queries:"
    )

    for query in (
        searchPlan.arxivQueries
    ):

        print(
            f"- {query}"
        )

    allResults = []

    # =================================================
    # 2. GENERAL WEB SEARCH
    # =================================================

    print(
        "\n=== WEB SEARCH ==="
    )

    for query in (
        searchPlan.webQueries
    ):

        print(
            f"\nSearching web:\n{query}"
        )

        try:

            results = webSearch(
                query,
                maxResults=5,
            )

            print(
                f"Found "
                f"{len(results)} "
                f"web results."
            )

            allResults.extend(
                results
            )

        except Exception as error:

            print(
                f"Web search failed for:\n"
                f"{query}"
            )

            print(
                error
            )

    # =================================================
    # 3. HUGGING FACE SEARCH
    # =================================================

    print(
        "\n=== HUGGING FACE SEARCH ==="
    )

    for query in (
        searchPlan.huggingFaceQueries
    ):

        print(
            "\nSearching Hugging Face:\n"
            f"{query}"
        )

        try:

            hfResults = (
                searchHuggingFaceModels(
                    query,
                    limit=20,
                )
            )

            print(
                f"Found "
                f"{len(hfResults)} "
                f"Hugging Face results "
                f"before filtering."
            )

            hfResults = (
                filterASRModels(
                    hfResults
                )
            )

            print(
                f"Found "
                f"{len(hfResults)} "
                f"Hugging Face ASR models "
                f"after filtering."
            )

            allResults.extend(
                hfResults
            )

        except Exception as error:

            print(
                "Hugging Face search failed."
            )

            print(
                error
            )

    # =================================================
    # 4. GITHUB SEARCH
    # =================================================

    print(
        "\n=== GITHUB SEARCH ==="
    )

    for query in (
        searchPlan.githubQueries
    ):

        print(
            "\nSearching GitHub:\n"
            f"{query}"
        )

        try:

            githubResults = (
                searchGithubRepositories(
                    query,
                    limit=10,
                )
            )

            print(
                f"Found "
                f"{len(githubResults)} "
                f"GitHub repositories."
            )

            allResults.extend(
                githubResults
            )

        except Exception as error:

            print(
                "GitHub search failed."
            )

            print(
                error
            )

    # =================================================
    # 5. ARXIV SEARCH
    # =================================================

    print(
        "\n=== ARXIV SEARCH ==="
    )

    for query in (
        searchPlan.arxivQueries
    ):

        print(
            "\nSearching arXiv:\n"
            f"{query}"
        )

        try:

            arxivResults = (
                searchArxivPapers(
                    query,
                    limit=10,
                )
            )

            print(
                f"Found "
                f"{len(arxivResults)} "
                f"arXiv papers."
            )

            allResults.extend(
                arxivResults
            )

        except Exception as error:

            print(
                "arXiv search failed."
            )

            print(
                error
            )

    # =================================================
    # 6. DEDUPLICATE INITIAL RESULTS
    # =================================================

    rawResultCount = (
        len(
            allResults
        )
    )

    allResults = (
        deduplicateResults(
            allResults
        )
    )

    print(
        f"\nRaw discovery results: "
        f"{rawResultCount}"
    )

    print(
        f"Unique discovery results: "
        f"{len(allResults)}"
    )

    # =================================================
    # 7. ADAPTIVE COVERAGE LOOP
    # =================================================

    maxExtraSearches = 3

    for searchRound in range(
        maxExtraSearches
    ):

        print(
            f"\n=== COVERAGE CHECK "
            f"{searchRound + 1} ==="
        )

        decision = (
            evaluateSearchResults(
                objective,
                allResults,
                cutoffDate,
                currentDate,
            )
        )

        if decision.enoughInformation:

            print(
                "\nDiscovery has enough "
                "information."
            )

            break

        if not decision.nextQuery:

            print(
                "\nMore information is required, "
                "but no additional query "
                "was provided."
            )

            break

        nextQuery = (
            decision.nextQuery
        )

        print(
            "\nAdditional search requested:"
        )

        print(
            nextQuery
        )

        try:

            newResults = webSearch(
                nextQuery,
                maxResults=5,
            )

            print(
                f"Found "
                f"{len(newResults)} "
                f"additional results."
            )

            allResults.extend(
                newResults
            )

            allResults = (
                deduplicateResults(
                    allResults
                )
            )

            print(
                f"Total unique discovery "
                f"results: "
                f"{len(allResults)}"
            )

        except Exception as error:

            print(
                "Additional web search failed."
            )

            print(
                error
            )

    # =================================================
    # 8. CROSS-SOURCE EVIDENCE MATCHING
    # =================================================

    print(
        "\n=== CROSS-SOURCE "
        "EVIDENCE MATCHING ==="
    )

    try:

        evidenceGroups = (
            groupModelEvidence(
                allResults
            )
        )

        print(
            f"Created "
            f"{len(evidenceGroups)} "
            f"evidence groups."
        )

    except Exception as error:

        print(
            "Cross-source evidence "
            "matching failed."
        )

        print(
            error
        )

        evidenceGroups = []

    # =================================================
    # 9. STRICT RECENCY FILTER
    # =================================================

    print(
        "\n=== RECENCY CHECK ==="
    )

    recentEvidenceGroups = []

    for group in evidenceGroups:

        releaseDate = (
            getModelReleaseDate(
                group
            )
        )

        isRecent = (
            checkRecency(
                releaseDate,
                days=30,
            )
        )

        modelName = (
            group.get(
                "modelName"
            )
        )

        print(
            f"{modelName}: "
            f"releaseDate={releaseDate}, "
            f"{'PASS' if isRecent else 'FAIL'}"
        )

        if not isRecent:
            continue

        group[
            "releaseDate"
        ] = releaseDate

        recentEvidenceGroups.append(
            group
        )

    evidenceGroups = (
        recentEvidenceGroups
    )

    print(
        f"\nEvidence groups within "
        f"{cutoffDate} to {currentDate}: "
        f"{len(evidenceGroups)}"
    )

    # =================================================
    # 10. FINAL CANDIDATE SELECTION
    # =================================================

    print(
        "\n=== CANDIDATE SELECTION ==="
    )

    response = llm.invoke(f"""
You are the Discovery Agent for an ASR technology scanner.

Current date:

{currentDate}

Strict release window:

{cutoffDate} to {currentDate}

Recent cross-source evidence groups:

{json.dumps(evidenceGroups, indent=2)}

The supplied evidence groups have already passed the
strict programmatic recency filter.

Your remaining job is ONLY to identify which groups
represent actual automatic speech recognition models
or model families.

Discovery has exactly two responsibilities:

1. Recency.
2. Actually ASR.

Recency has already been checked before this step.

Select up to 5 candidates.

A valid candidate MUST:

1. Be an automatic speech recognition model or model family.

2. Be an actual model/model-family release rather than:

   - general articles
   - tutorials
   - surveys
   - software libraries
   - toolkits
   - leaderboards
   - unrelated speech systems

3. Be identifiable from the supplied evidence.

4. Not return the same model multiple times.

Important evidence-grouping rule:

A fine-tuned, adapted, distilled, quantized, converted,
or otherwise derived model is NOT automatically the same
model as its base model.

For example:

A model with metadata such as:

base_model:SomeOrg/BaseModel

or:

base_model:finetune:SomeOrg/BaseModel

should be treated as a separately released model if it
has its own model identity.

Do not collapse such a model into its base model merely
because they are related.

Avoid returning:

- general ASR toolkits
- software libraries
- tutorials
- surveys
- leaderboards
- generic articles
- unrelated speech systems
- paper-only methods without an identifiable model
  or model family

candidate_type must be one of:

- "model"
- "model_family"
- "toolkit"
- "paper_only"
- "unknown"

Prefer:

- "model"
- "model_family"

The reason field should ONLY explain why this is
an actual ASR model or model family.

Do NOT investigate or make claims about:

- public model weights
- source-code availability
- local deployability
- licensing
- architecture
- parameter counts
- language counts
- WER or CER
- benchmarks
- training data
- fine-tuning support
- hardware requirements
- deployment requirements

Those belong to the Research Agent.

Do not fabricate models.

Do not return a candidate unless there is supporting
evidence in the supplied discovery data.

For sourceUrl, choose the most useful source for
identifying the model.

Prefer:

1. Hugging Face model page
2. official project page
3. official GitHub repository
4. official research page
5. arXiv paper

Return ONLY valid JSON.

Use exactly this structure:

{{
    "candidates": [
        {{
            "name": "model name",
            "organisation": "organisation or null",
            "sourceUrl": "primary URL or null",
            "reason": "short discovery reason",
            "candidate_type": "model"
        }}
    ]
}}

Do not include markdown.
Do not include code fences.
Do not include explanations outside the JSON.
""")

    # =================================================
    # 11. PARSE LLM OUTPUT
    # =================================================

    rawContent = (
        response.content
    )

    print(
        "\n=== RAW DISCOVERY RESPONSE ==="
    )

    print(
        rawContent
    )

    data = json.loads(
        rawContent
    )

    # =================================================
    # 12. VALIDATE USING PYDANTIC
    # =================================================

    validated = (
        CandidateList.model_validate(
            data
        )
    )

    candidates = [
        candidate.model_dump()
        for candidate in validated.candidates
    ]

    print(
        f"\nValidated candidates: "
        f"{len(candidates)}"
    )

    # =================================================
    # 13. TEMPORARILY CHOOSE FIRST CANDIDATE
    # =================================================

    currentModel = (
        candidates[0]
        if candidates
        else {}
    )

    # =================================================
    # 14. RETURN LANGGRAPH STATE UPDATE
    # =================================================

    return {
        "candidates": candidates,
        "currentModel": currentModel,
    }