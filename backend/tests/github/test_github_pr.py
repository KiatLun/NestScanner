import base64
import os
import sys
import uuid

from pathlib import Path
from urllib.parse import quote

import requests
from dotenv import load_dotenv

# ============================================================
# Configuration
# ============================================================

BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env")

TOKEN = os.getenv("GITHUB_TOKEN")
OWNER = os.getenv("ECHOFORGE_GITHUB_OWNER")
REPO = os.getenv("ECHOFORGE_GITHUB_REPO")

testResults = {}

session = requests.Session()
session.headers.update(
    {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
)


# ============================================================
# Helpers
# ============================================================


def printSection(title: str):

    print()
    print("=" * 65)
    print(title)
    print("=" * 65)


def recordResult(
    name: str,
    passed: bool,
    error: str | None = None,
):

    testResults[name] = {
        "passed": passed,
        "error": error,
    }

    print(f"[{'PASS' if passed else 'FAIL'}] {name}")

    if error:
        print(f"       {error}")


def githubRequest(
    method: str,
    endpoint: str,
    **kwargs,
):

    response = session.request(
        method,
        f"https://api.github.com{endpoint}",
        timeout=30,
        **kwargs,
    )

    print(f"[GitHub] {method} {endpoint}: " f"HTTP {response.status_code}")

    if not response.ok:
        raise RuntimeError(f"HTTP {response.status_code}: " f"{response.text[:500]}")

    if response.status_code == 204:
        return None

    return response.json()


# ============================================================
# GitHub connection
# ============================================================


def testConnection() -> dict:

    printSection("GITHUB CONNECTION TEST")

    requiredVariables = {
        "GITHUB_TOKEN": TOKEN,
        "ECHOFORGE_GITHUB_OWNER": OWNER,
        "ECHOFORGE_GITHUB_REPO": REPO,
    }

    missing = [name for name, value in requiredVariables.items() if not value]

    if missing:
        raise RuntimeError("Missing environment variables: " + ", ".join(missing))

    recordResult("Environment configuration", True)

    user = githubRequest("GET", "/user")
    print("Authenticated as:", user["login"])
    recordResult("GitHub authentication", True)

    repoApi = f"/repos/{OWNER}/{REPO}"

    repository = githubRequest("GET", repoApi)
    print("Repository:", repository["full_name"])
    print("Private:", repository["private"])
    recordResult("Repository access", True)

    baseBranch = repository["default_branch"]

    branch = githubRequest(
        "GET",
        f"{repoApi}/branches/" f"{quote(baseBranch, safe='')}",
    )

    baseSha = branch["commit"]["sha"]

    print("Default branch:", baseBranch)
    print("Latest commit:", baseSha)

    recordResult("Default branch access", True)

    return {
        "baseBranch": baseBranch,
        "baseSha": baseSha,
    }


# ============================================================
# Actual PR creation and automatic cleanup
# ============================================================


def testPullRequest(
    baseBranch: str,
    baseSha: str,
):

    printSection("GITHUB PR CREATION TEST")

    testId = uuid.uuid4().hex[:8]

    branchName = f"nestscanner/pr-test-{testId}"
    filePath = f"docs/nestscanner-pr-test-{testId}.md"

    repoApi = f"/repos/{OWNER}/{REPO}"

    branchCreated = False
    prNumber = None
    currentStep = "Branch creation"
    cleanupErrors = []

    try:

        # ----------------------------------------
        # 1. Create real temporary branch
        # ----------------------------------------

        githubRequest(
            "POST",
            f"{repoApi}/git/refs",
            json={
                "ref": f"refs/heads/{branchName}",
                "sha": baseSha,
            },
        )

        branchCreated = True
        recordResult("Branch creation", True)

        # ----------------------------------------
        # 2. Commit real test file
        # ----------------------------------------

        currentStep = "File commit"

        content = (
            "# NestScanner GitHub PR Test\n\n"
            "Temporary file used to verify "
            "GitHub PR creation and cleanup.\n"
        )

        encodedContent = base64.b64encode(content.encode("utf-8")).decode("ascii")

        githubRequest(
            "PUT",
            f"{repoApi}/contents/{filePath}",
            json={
                "message": "test: verify NestScanner PR",
                "content": encodedContent,
                "branch": branchName,
            },
        )

        recordResult("File commit", True)

        # ----------------------------------------
        # 3. Create real draft PR
        # ----------------------------------------

        currentStep = "Draft PR creation"

        pullRequest = githubRequest(
            "POST",
            f"{repoApi}/pulls",
            json={
                "title": (f"test: NestScanner GitHub PR {testId}"),
                "head": branchName,
                "base": baseBranch,
                "draft": True,
                "body": (
                    "Temporary integration test PR.\n\n"
                    "Automatically closed after testing. "
                    "Do not merge."
                ),
            },
        )

        prNumber = pullRequest["number"]

        print("PR URL:", pullRequest["html_url"])
        recordResult("Draft PR creation", True)

    except Exception as error:

        recordResult(
            currentStep,
            False,
            str(error),
        )

    finally:

        # ----------------------------------------
        # 4. Always attempt cleanup
        # ----------------------------------------

        printSection("AUTOMATIC CLEANUP")

        if prNumber is not None:

            try:

                githubRequest(
                    "PATCH",
                    f"{repoApi}/pulls/{prNumber}",
                    json={"state": "closed"},
                )

                recordResult("PR closure", True)

            except Exception as error:

                recordResult(
                    "PR closure",
                    False,
                    str(error),
                )

                cleanupErrors.append(error)

        if branchCreated:

            try:

                githubRequest(
                    "DELETE",
                    f"{repoApi}/git/refs/heads/" f"{quote(branchName, safe='/')}",
                )

                recordResult("Branch deletion", True)

            except Exception as error:

                recordResult(
                    "Branch deletion",
                    False,
                    str(error),
                )

                cleanupErrors.append(error)

        if cleanupErrors:
            print(
                "\nWARNING: Cleanup incomplete. "
                "Check GitHub for the temporary "
                "PR or branch."
            )


# ============================================================
# Final summary
# ============================================================


def printSummary() -> bool:

    printSection("GITHUB INTEGRATION TEST SUMMARY")

    expectedTests = [
        "Environment configuration",
        "GitHub authentication",
        "Repository access",
        "Default branch access",
        "Branch creation",
        "File commit",
        "Draft PR creation",
        "PR closure",
        "Branch deletion",
    ]

    passed = 0
    failed = 0

    for name in expectedTests:

        result = testResults.get(name)

        if result is None:
            print(f"  SKIP  {name}")
            failed += 1

        elif result["passed"]:
            print(f"  PASS  {name}")
            passed += 1

        else:
            print(f"  FAIL  {name}")
            print(f"        {result['error']}")
            failed += 1

    print()
    print(f"Passed: {passed}")
    print(f"Failed or incomplete: {failed}")

    print()

    if failed == 0:
        print("=" * 65)
        print("RESULT: PASS")
        print("PR created, closed and temporary " "branch deleted successfully.")
        print("=" * 65)
        return True

    print("=" * 65)
    print("RESULT: FAIL")
    print("=" * 65)

    return False


# ============================================================
# Main
# ============================================================


def main():

    printSection("FULL GITHUB INTEGRATION TEST")

    try:

        connection = testConnection()

        testPullRequest(
            baseBranch=connection["baseBranch"],
            baseSha=connection["baseSha"],
        )

    except Exception as error:

        print(
            "\n[GitHub Test] Error:",
            str(error),
        )

    finally:

        success = printSummary()

        if not success:
            sys.exit(1)


if __name__ == "__main__":
    main()
