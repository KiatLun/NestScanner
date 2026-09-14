import json
import re

from app.llm.client import getLLM

from app.agents.downloaderBuilder.prompts import (
    buildDownloaderGenerationPrompt,
    buildDownloaderRepairPrompt,
)

from app.services.echoforge.generatedDownloaderManager import (
    validateDownloaderFiles,
    writeDownloaderFiles,
    runGeneratedDownloader,
)


def parseLLMJson(
    content: str,
) -> dict:

    content = content.strip()

    if content.startswith("```"):

        lines = content.splitlines()

        if lines:
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        content = "\n".join(lines).strip()

    return json.loads(content)


def sanitizeDownloaderName(
    value: str,
) -> str:

    value = value.strip().lower()

    value = re.sub(
        r"[^a-z0-9_]+",
        "_",
        value,
    )

    value = value.strip("_")

    if not value.endswith("_download"):
        value += "_download"

    if not value:
        raise ValueError("Invalid downloader name.")

    return value


def sanitizeSimpleName(
    value: str,
) -> str:

    value = value.strip()

    value = re.sub(
        r"[^A-Za-z0-9._-]+",
        "-",
        value,
    )

    value = value.strip("-")

    if not value:
        raise ValueError("Invalid generated name.")

    return value


def generateDownloaderPlan(
    researchResult: dict,
    downloadDecision: dict,
) -> dict:

    llm = getLLM()

    prompt = buildDownloaderGenerationPrompt(
        researchResult,
        downloadDecision,
    )

    response = llm.invoke(prompt)

    plan = parseLLMJson(response.content)

    requiredFields = {
        "downloaderName",
        "modelListName",
        "cacheName",
        "files",
    }

    missingFields = requiredFields - set(plan.keys())

    if missingFields:

        raise ValueError(
            "Downloader Builder response " "missing fields: " f"{sorted(missingFields)}"
        )

    plan["downloaderName"] = sanitizeDownloaderName(plan["downloaderName"])

    plan["modelListName"] = sanitizeSimpleName(plan["modelListName"])

    plan["cacheName"] = sanitizeSimpleName(plan["cacheName"])

    validateDownloaderFiles(plan["files"])

    return plan


def repairDownloaderPlan(
    researchResult: dict,
    downloadDecision: dict,
    downloaderPlan: dict,
    attemptResult: dict,
) -> dict:

    llm = getLLM()

    prompt = buildDownloaderRepairPrompt(
        researchResult,
        downloadDecision,
        downloaderPlan,
        attemptResult,
    )

    response = llm.invoke(prompt)

    repairResult = parseLLMJson(response.content)

    files = repairResult.get("files")

    validateDownloaderFiles(files)

    return {
        **downloaderPlan,
        "reason": repairResult.get(
            "reason",
            downloaderPlan.get("reason"),
        ),
        "files": files,
    }


def downloaderBuilderAgent(
    researchResult: dict,
    downloadDecision: dict,
    maxAttempts: int = 3,
) -> dict:

    if maxAttempts < 1:
        raise ValueError("maxAttempts must be at least 1.")

    modelName = downloadDecision["modelName"]

    print()
    print("=" * 60)
    print("[Downloader Builder] Starting: " f"{modelName}")
    print("=" * 60)

    # ----------------------------------------
    # 1. Generate initial downloader
    # ----------------------------------------

    downloaderPlan = generateDownloaderPlan(
        researchResult,
        downloadDecision,
    )

    downloaderName = downloaderPlan["downloaderName"]

    modelListName = downloaderPlan["modelListName"]

    cacheName = downloaderPlan["cacheName"]

    print("[Downloader Builder] Generated: " f"{downloaderName}")

    writeDownloaderFiles(
        downloaderName=downloaderName,
        files=downloaderPlan["files"],
        allowOverwrite=False,
    )

    lastAttemptResult = None

    # ----------------------------------------
    # 2. Test / repair loop
    # ----------------------------------------

    for attempt in range(
        1,
        maxAttempts + 1,
    ):

        print()
        print("[Downloader Builder] " f"Attempt {attempt}/{maxAttempts}")

        attemptResult = runGeneratedDownloader(
            downloaderName=downloaderName,
            modelListName=modelListName,
            cacheName=cacheName,
        )

        lastAttemptResult = attemptResult

        # ------------------------------------
        # Success
        # ------------------------------------

        if attemptResult["success"]:

            print("[Downloader Builder] " "Downloader succeeded.")

            return {
                "status": "downloader-created",
                "modelName": modelName,
                "sourceType": (downloadDecision["sourceType"]),
                "source": (downloadDecision["source"]),
                "downloader": downloaderName,
                "modelListName": modelListName,
                "cacheName": cacheName,
                "cachePath": (attemptResult["cachePath"]),
                "attempts": attempt,
            }

        # ------------------------------------
        # No attempts remaining
        # ------------------------------------

        if attempt == maxAttempts:
            break

        print("[Downloader Builder] " "Attempt failed. " "Requesting repair.")

        # ------------------------------------
        # LLM repair
        # ------------------------------------

        downloaderPlan = repairDownloaderPlan(
            researchResult,
            downloadDecision,
            downloaderPlan,
            attemptResult,
        )

        writeDownloaderFiles(
            downloaderName=downloaderName,
            files=downloaderPlan["files"],
            allowOverwrite=True,
        )

    # ----------------------------------------
    # 3. Failed after all attempts
    # ----------------------------------------

    return {
        "status": "downloader-build-failed",
        "modelName": modelName,
        "sourceType": (downloadDecision["sourceType"]),
        "source": (downloadDecision["source"]),
        "downloader": downloaderName,
        "modelListName": modelListName,
        "cacheName": cacheName,
        "attempts": maxAttempts,
        "error": (
            lastAttemptResult.get(
                "output",
                "",
            )
            if lastAttemptResult
            else ""
        ),
    }
