import json
import re

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.llm.client import getLLM

from app.tools.webSearch import (
    webSearch,
    deduplicateResults,
)


llm = getLLM()


def checkRecency(
    candidate: dict,
    discoveryEvidence: list[dict],
    days: int = 60,
    maxSearches: int = 3,
) -> dict:
    """
    Determine whether an ASR candidate was released
    within the required recency window.

    Start with Discovery evidence.

    If an explicit release date is directly stated,
    extract it deterministically.

    Otherwise, use the existing LLM + targeted search
    process.

    Stop when:
    - a release date is found, or
    - maxSearches is reached.

    Returns:
    {
        "releaseDate": str | None,
        "isRecent": bool,
        "evidence": list[dict]
    }
    """

    currentDate = datetime.now(
        ZoneInfo("Asia/Singapore")
    ).date()

    evidence = list(
        discoveryEvidence
    )

    searchCount = 0

    while True:

        # =================================================
        # 1. TRY EXPLICIT RELEASE DATE EXTRACTION
        # =================================================

        releaseDate = extractExplicitReleaseDate(
            candidate,
            evidence,
        )

        if releaseDate:
            return {
                "releaseDate": releaseDate,
                "isRecent": calculateRecency(
                    releaseDate,
                    currentDate,
                    days,
                ),
                "evidence": evidence,
            }

        # =================================================
        # 2. EVALUATE CURRENT EVIDENCE USING LLM
        # =================================================

        decision = evaluateRecency(
            candidate,
            evidence,
        )

        releaseDate = decision.get(
            "releaseDate"
        )

        # =================================================
        # 3. RELEASE DATE FOUND BY LLM
        # =================================================

        if releaseDate:
            isRecent = calculateRecency(
                releaseDate,
                currentDate,
                days,
            )

            return {
                "releaseDate": releaseDate,
                "isRecent": isRecent,
                "evidence": evidence,
            }

        # =================================================
        # 4. STOP IF SEARCH LIMIT REACHED
        # =================================================

        if searchCount >= maxSearches:
            return {
                "releaseDate": None,
                "isRecent": False,
                "evidence": evidence,
            }

        # =================================================
        # 5. GET NEXT TARGETED QUERY
        # =================================================

        nextQuery = decision.get(
            "nextQuery"
        )

        if not nextQuery:
            return {
                "releaseDate": None,
                "isRecent": False,
                "evidence": evidence,
            }

        print(
            f"\nRecency search "
            f"{searchCount + 1}: "
            f"{nextQuery}"
        )

        # =================================================
        # 6. SEARCH
        # =================================================

        try:
            results = webSearch(
                nextQuery,
                maxResults=5,
            )

            evidence.extend(
                results
            )

            evidence = deduplicateResults(
                evidence
            )

        except Exception as error:
            print(
                f"Recency search failed: "
                f"{nextQuery}"
            )

            print(error)

        searchCount += 1


def extractExplicitReleaseDate(
    candidate: dict,
    evidence: list[dict],
) -> str | None:
    """
    Extract an explicit release date only when the
    evidence clearly mentions the candidate and directly
    ties a date to release wording.

    This is intentionally conservative so it does not
    interfere with cases already handled well by the LLM.
    """

    modelName = (
        candidate.get(
            "name",
            "",
        )
        or ""
    ).lower()

    if not modelName:
        return None

    releasePatterns = [
        r"released on ([A-Za-z]+ \d{1,2}, \d{4})",
        r"was released on ([A-Za-z]+ \d{1,2}, \d{4})",
        r"launched on ([A-Za-z]+ \d{1,2}, \d{4})",
        r"introduced on ([A-Za-z]+ \d{1,2}, \d{4})",
        r"became available on ([A-Za-z]+ \d{1,2}, \d{4})",
    ]

    for item in evidence:
        title = (
            item.get(
                "title",
                "",
            )
            or ""
        )

        description = (
            item.get(
                "description",
                "",
            )
            or ""
        )

        text = (
            f"{title} {description}"
        )

        lowerText = text.lower()

        # Only use this deterministic shortcut if
        # the exact candidate name appears in the evidence.
        if modelName not in lowerText:
            continue

        for pattern in releasePatterns:
            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if not match:
                continue

            rawDate = match.group(1)

            for dateFormat in [
                "%B %d, %Y",
                "%b %d, %Y",
            ]:
                try:
                    parsedDate = datetime.strptime(
                        rawDate,
                        dateFormat,
                    ).date()

                    return parsedDate.isoformat()

                except ValueError:
                    continue

    return None


def evaluateRecency(
    candidate: dict,
    evidence: list[dict],
) -> dict:
    """
    Determine whether the current evidence establishes
    the candidate's actual release date.

    If not, generate one targeted search query.
    """

    response = llm.invoke(f"""
You are researching the release date of an automatic
speech recognition model.

Candidate:

{json.dumps(candidate, indent=2)}

Evidence currently available:

{json.dumps(evidence, indent=2)}


YOUR TASK

Determine whether the current evidence establishes the
actual release date of THIS candidate.

The candidate may be:

- an individual model
- a specific model variant
- a model family


==================================================
ACCEPT A RELEASE DATE WHEN
==================================================

Accept a date when a supplied source explicitly states
that THIS exact candidate:

- "was released on ..."
- "released on ..."
- "we release ..."
- "launched on ..."
- "introduced on ..."
- "became available on ..."
- "model weights were released on ..."
- "is released on ..."

The release wording must clearly refer to the model or
model family itself.

If the wording clearly refers to THIS exact candidate,
you MAY accept the date even if the source is
third-party.

Official sources are preferred, but they are NOT
required when an existing source clearly and
unambiguously states the release date.

Do NOT continue searching merely because the source
is not official.


==================================================
SOURCE PREFERENCE
==================================================

When multiple sources exist, prefer:

1. official organisation announcement
2. official model or project page
3. official GitHub repository
4. official Hugging Face repository
5. research paper or project page
6. reputable third-party reporting

However, a clear third-party statement such as:

"MODEL was released on July 28, 2026"

is sufficient unless there is contradictory evidence.


==================================================
DO NOT ACCEPT
==================================================

Do NOT treat these as the model release date:

- article publication date by itself
- webpage update date
- GitHub last update date
- Hugging Face lastModified
- search result retrieval date
- benchmark date
- dates referring to another model
- dates referring to another organisation
- dates referring to a different model variant

For example:

If the candidate is:

Qwen3-ASR

and the evidence only states:

Qwen3-ASR-1.7B was released on January 29, 2026

do NOT automatically assume that January 29 is the
release date of the entire Qwen3-ASR family unless the
evidence indicates the family was released together.


==================================================
MODEL IDENTITY
==================================================

Make sure the release date belongs to THIS candidate.

Use:

- candidate name
- organisation
- model family
- variant name
- surrounding ASR context

Do not accept a date just because another model has a
similar name.


==================================================
IF RELEASE DATE IS FOUND
==================================================

Return:

{{
    "releaseDate": "YYYY-MM-DD",
    "nextQuery": null
}}


==================================================
IF RELEASE DATE IS NOT FOUND
==================================================

Generate ONE targeted web search query that is most
likely to find the release date.

The query should use:

- the exact candidate name
- organisation when available
- "release"
- "launch"
- "announcement"
- ASR or speech recognition when useful

Prefer a specific query rather than a broad one.

Good examples:

"Useful Sensors Moonshine ASR release date"

"Cohere cohere-transcribe-03-2026 release"

"Qwen Qwen3-ASR official release announcement"

"NVIDIA Nemotron 3.5 ASR streaming release"


Return:

{{
    "releaseDate": null,
    "nextQuery": "targeted query"
}}


Return ONLY valid JSON.
Do not include markdown.
Do not include code fences.
Do not include explanations outside the JSON.
""")

    try:
        return json.loads(
            response.content
        )

    except json.JSONDecodeError:
        return {
            "releaseDate": None,
            "nextQuery": None,
        }


def calculateRecency(
    releaseDate: str,
    currentDate,
    days: int,
) -> bool:
    """
    Deterministically determine whether releaseDate
    is within the configured recency window.
    """

    try:
        parsedDate = datetime.strptime(
            releaseDate,
            "%Y-%m-%d",
        ).date()

    except ValueError:
        return False

    cutoffDate = (
        currentDate
        - timedelta(
            days=days
        )
    )

    return (
        cutoffDate
        <= parsedDate
        <= currentDate
    )