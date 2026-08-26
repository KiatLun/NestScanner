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
    Return the recent-source discovery window
    using Singapore local time.

    Discovery uses this only to guide searches toward
    recent evidence.

    Actual model release-date verification belongs
    to the Research Agent.
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
    Check whether current search results contain enough
    likely recent ASR candidates.

    Discovery does not verify the actual model release date.
    """

    response = llm.invoke(f"""
You are evaluating search coverage for an ASR technology scanner.

Objective:

{objective}

Current date:

{currentDate}

Recent discovery window:

{cutoffDate} to {currentDate}

Current discovery evidence:

{json.dumps(searchResults, indent=2)}

The Discovery Agent has two responsibilities:

1. Find likely ASR model or model-family candidates from
   recent sources.

2. Ensure that the candidates appear to actually be
   automatic speech recognition models.

IMPORTANT:

Discovery does NOT need to establish the true model
release date.

Release-date verification belongs to the Research Agent.

Your job here is ONLY to decide whether the current
search results provide enough coverage to identify
several likely ASR candidates worth researching.

Check:

1. Are several identifiable ASR models or model families
   represented?

2. Are there multiple distinct candidate models?

3. Are recent sources from approximately
   {cutoffDate} to {currentDate} represented?

4. Are the results mostly relevant to automatic speech
   recognition?

5. Are the results dominated by irrelevant items such as:

   - tutorials
   - surveys
   - software libraries
   - generic articles
   - unrelated speech systems

6. Is there enough evidence to pass likely candidates
   to the Research Agent?

Important:

- Use the current date supplied above.
- Do NOT assume that a recent article means the model
  itself was recently released.
- Do NOT attempt to verify the true model release date.
- Do NOT investigate technical details.

Do NOT investigate:

- actual release date
- public model weights
- source-code availability
- local deployability
- licensing
- architecture
- benchmarks
- parameter counts
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

- target recent ASR model announcements, repositories,
  papers, or releases
- focus approximately on {cutoffDate} to {currentDate}

Return ONLY valid JSON.

Do not include markdown.
Do not include code fences.
Do not include explanations outside the JSON.
""")

    rawContent = response.content

    print(
        "\n=== SEARCH COVERAGE DECISION ==="
    )

    print(rawContent)

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
    Discover likely recent ASR model candidates.

    Discovery is responsible only for:

    1. Finding likely ASR models/model families from
       recent sources.

    2. Checking that they are actually ASR.

    Actual release-date verification and deeper technical
    investigation belong to Research.
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
        f"\nRecent discovery window: "
        f"{cutoffDate} to {currentDate}"
    )

    # =================================================
    # 1. BUILD SOURCE-SPECIFIC SEARCH PLAN
    # =================================================

    searchObjective = f"""
{objective}

Current date: {currentDate}

Find likely automatic speech recognition models or
model families appearing in recent sources approximately
between {cutoffDate} and {currentDate}.

The purpose of this stage is candidate discovery.

Do NOT attempt to prove that the model itself was
released during this period.

A recent repository update, model-card edit, article,
paper, or announcement may be useful discovery evidence,
but the actual model release date will be verified later
by the Research Agent.
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

            print(error)

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

            print(error)

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

            print(error)

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

            print(error)

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

            print(error)

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

        print(error)

        evidenceGroups = []

    # =================================================
    # 9. FINAL ASR CANDIDATE SELECTION
    # =================================================

    print(
        "\n=== CANDIDATE SELECTION ==="
    )

    response = llm.invoke(f"""
You are the Discovery Agent for an ASR technology scanner.

Current date:

{currentDate}

Recent discovery window:

{cutoffDate} to {currentDate}

Cross-source evidence groups:

{json.dumps(evidenceGroups, indent=2)}

Your job is ONLY to identify which groups represent
actual automatic speech recognition models or model
families that are worth passing to the Research Agent.

Discovery does NOT verify the actual model release date.

The Research Agent will later determine:

- the true model release date
- whether the model satisfies the required recency window
- legitimacy
- local deployability
- technical details

Select up to 5 candidates.

A valid candidate MUST:

1. Be an automatic speech recognition model or
   model family.

2. Be an actual model/model-family identity rather than:

   - general articles
   - tutorials
   - surveys
   - software libraries
   - toolkits
   - leaderboards
   - unrelated speech systems

3. Be identifiable from the supplied evidence.

4. Have enough evidence to justify deeper investigation.

5. Not return the same model multiple times.

Important:

A fine-tuned, adapted, distilled, quantized, converted,
or otherwise derived model is NOT automatically the same
model as its base model.

For example:

base_model:SomeOrg/BaseModel

or:

base_model:finetune:SomeOrg/BaseModel

indicates a relationship.

It does NOT mean both are the same model release.

A separately named derived model should remain a
separate candidate when it has its own model identity.

Do NOT reject a model merely because its actual release
date is not yet known.

Release-date verification belongs to Research.

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

The reason field should ONLY explain why this appears
to be an actual ASR model or model family worth
investigating.

Do NOT make claims about:

- actual model release date
- whether it passes the 30-day requirement
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

For sourceUrl, choose the most useful source for
identifying the model.

Prefer:

1. Hugging Face model page
2. official project page
3. official GitHub repository
4. official research page
5. arXiv paper
6. credible announcement/article

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
    # 10. PARSE LLM OUTPUT
    # =================================================

    rawContent = (
        response.content
    )

    print(
        "\n=== RAW DISCOVERY RESPONSE ==="
    )

    print(rawContent)

    data = json.loads(
        rawContent
    )

    # =================================================
    # 11. VALIDATE USING PYDANTIC
    # =================================================

    validated = (
        CandidateList.model_validate(
            data
        )
    )

    candidates = [
        candidate.model_dump()
        for candidate
        in validated.candidates
    ]

    print(
        f"\nValidated candidates: "
        f"{len(candidates)}"
    )

    # =================================================
    # 12. TEMPORARILY CHOOSE FIRST CANDIDATE
    # =================================================

    currentModel = (
        candidates[0]
        if candidates
        else {}
    )

    # =================================================
    # 13. RETURN LANGGRAPH STATE UPDATE
    # =================================================

    return {
        "candidates": candidates,
        "currentModel": currentModel,
    }