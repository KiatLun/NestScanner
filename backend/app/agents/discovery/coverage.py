import json

from app.llm.client import getLLM

from app.models.schemas import (
    DiscoveryDecision,
)

from app.agents.discovery.search import (
    getDiscoveryDateWindow,
)

from app.tools.webSearch import (
    webSearch,
    deduplicateResults,
)


llm = getLLM()


def prepareCoverageEvidence(
    evidence: list[dict],
) -> list[dict]:
    """
    Produce a compact representation for the coverage
    decision only.

    This does NOT alter the evidence later sent to the
    evidence matcher.
    """

    compactEvidence = []

    for result in evidence:

        description = (
            result.get(
                "description",
                "",
            )
            or ""
        )

        compactEvidence.append({
            "source": result.get(
                "source"
            ),
            "title": result.get(
                "title"
            ),
            "url": result.get(
                "url"
            ),
            "description": (
                description[:500]
            ),
        })

    return compactEvidence


def evaluateDiscoveryCoverage(
    objective: str,
    evidence: list[dict],
) -> DiscoveryDecision:
    """
    Decide whether Discovery has enough evidence
    to proceed to candidate selection.
    """

    cutoffDate, currentDate = (
        getDiscoveryDateWindow()
    )

    compactEvidence = (
        prepareCoverageEvidence(
            evidence
        )
    )

    response = llm.invoke(f"""
You are evaluating search coverage for an ASR
technology scanner.

Objective:

{objective}

Current date:

{currentDate}

Recent discovery window:

{cutoffDate} to {currentDate}

Current evidence:

{json.dumps(compactEvidence, indent=2)}

The Discovery Agent is scouting likely automatic
speech recognition models or model families.

Discovery does NOT verify the true release date.

Release-date verification belongs to Research.

Determine whether there is enough evidence to proceed.

Check:

1. Are several identifiable ASR models or model
   families represented?

2. Are multiple distinct candidates represented?

3. Are recent ASR-related sources represented?

4. Is the evidence sufficiently relevant to ASR?

5. Is there enough information to identify candidates
   worth deeper research?

Do NOT investigate:

- actual model release date
- licensing
- local deployment
- model weights
- architecture
- parameter count
- WER
- benchmarks
- hardware
- fine-tuning

If there is enough information, return:

{{
    "enoughInformation": true,
    "nextQuery": null
}}

If another search would meaningfully improve Discovery,
return:

{{
    "enoughInformation": false,
    "nextQuery": "one targeted web search query"
}}

Only request another search when it is actually useful.

Return ONLY valid JSON.

Do not include markdown.
Do not include code fences.
Do not include explanations outside the JSON.
""")

    data = json.loads(
        response.content
    )

    return DiscoveryDecision.model_validate(
        data
    )


def improveDiscoveryCoverage(
    objective: str,
    evidence: list[dict],
    maxExtraSearches: int = 3,
) -> list[dict]:
    """
    Adaptively perform additional targeted searches
    when current Discovery coverage is insufficient.
    """

    for searchRound in range(
        maxExtraSearches
    ):

        print(
            f"\n=== COVERAGE CHECK "
            f"{searchRound + 1} ==="
        )

        decision = (
            evaluateDiscoveryCoverage(
                objective,
                evidence,
            )
        )

        print(
            f"Enough information: "
            f"{decision.enoughInformation}"
        )

        if decision.enoughInformation:
            break

        if not decision.nextQuery:
            break

        print(
            "\nAdditional search requested:"
        )

        print(
            decision.nextQuery
        )

        try:
            newEvidence = webSearch(
                decision.nextQuery,
                maxResults=5,
            )

            print(
                f"Found {len(newEvidence)} "
                "additional results."
            )

            evidence.extend(
                newEvidence
            )

            evidence = deduplicateResults(
                evidence
            )

        except Exception as error:
            print(
                "Additional discovery search failed."
            )

            print(error)

            break

    return evidence