import os

import requests

from dotenv import load_dotenv

from urllib.parse import quote


load_dotenv()


GITHUB_TOKEN = os.getenv(
    "GITHUB_TOKEN"
)


# ============================================================
# Shared GitHub headers
# ============================================================

def getGitHubHeaders() -> dict:

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "NestScanner",
    }

    if GITHUB_TOKEN:

        headers[
            "Authorization"
        ] = (
            f"Bearer {GITHUB_TOKEN}"
        )

    return headers


# ============================================================
# Authentication check
# ============================================================

def checkGitHubAuthentication() -> bool:
    """
    Check whether the configured GitHub token is valid.

    Returns:
        True  -> authenticated successfully
        False -> no valid authentication
    """

    if not GITHUB_TOKEN:

        print(
            "GitHub authentication check: "
            "GITHUB_TOKEN is not configured."
        )

        return False

    url = (
        "https://api.github.com/user"
    )

    try:

        response = requests.get(
            url,
            headers=getGitHubHeaders(),
            timeout=30,
        )

        if response.status_code == 200:

            userData = response.json()

            username = userData.get(
                "login",
                "unknown",
            )

            print(
                "GitHub authentication "
                f"successful: {username}"
            )

            return True

        if response.status_code == 401:

            print(
                "GitHub authentication failed: "
                "invalid or expired GITHUB_TOKEN."
            )

            return False

        print(
            "GitHub authentication check "
            f"returned HTTP {response.status_code}."
        )

        return False

    except requests.RequestException as error:

        print(
            "GitHub authentication check "
            "failed:"
        )

        print(error)

        return False


# ============================================================
# Repository search
# ============================================================

def searchGitHubRepositories(
    query: str,
    limit: int = 10,
) -> list[dict]:

    url = (
        "https://api.github.com/"
        "search/repositories"
    )

    params = {
        "q": query,
        "per_page": limit,
        "sort": "updated",
        "order": "desc",
    }

    response = requests.get(
        url,
        headers=getGitHubHeaders(),
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    results = []

    for repo in data.get(
        "items",
        [],
    ):

        results.append(
            {
                "source": "github",

                "title": repo.get(
                    "full_name"
                ),

                "url": repo.get(
                    "html_url"
                ),

                "description": repo.get(
                    "description"
                ),

                "metadata": {

                    "repositoryId": repo.get(
                        "full_name"
                    ),

                    "stars": repo.get(
                        "stargazers_count"
                    ),

                    "language": repo.get(
                        "language"
                    ),

                    "createdAt": repo.get(
                        "created_at"
                    ),

                    "updatedAt": repo.get(
                        "updated_at"
                    ),

                    "defaultBranch": repo.get(
                        "default_branch"
                    ),

                    "topics": repo.get(
                        "topics",
                        [],
                    ),
                },
            }
        )

    return results


# ============================================================
# Repository metadata
# ============================================================

def getGitHubRepository(
    owner: str,
    repository: str,
) -> dict:

    url = (
        "https://api.github.com/repos/"
        f"{owner}/{repository}"
    )

    response = requests.get(
        url,
        headers=getGitHubHeaders(),
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# Repository file tree
# ============================================================

def getGitHubRepositoryFiles(
    owner: str,
    repository: str,
    branch: str | None = None,
) -> list[str]:

    if branch is None:

        repositoryInfo = (
            getGitHubRepository(
                owner=owner,
                repository=repository,
            )
        )

        branch = (
            repositoryInfo.get(
                "default_branch",
                "main",
            )
        )

    url = (
        "https://api.github.com/repos/"
        f"{owner}/{repository}/git/trees/"
        f"{quote(branch, safe='')}"
    )

    params = {
        "recursive": "1",
    }

    response = requests.get(
        url,
        headers=getGitHubHeaders(),
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    paths = []

    for item in data.get(
        "tree",
        [],
    ):

        if item.get("type") != "blob":
            continue

        path = item.get(
            "path"
        )

        if path:

            paths.append(
                path
            )

    return paths


# ============================================================
# File content
# ============================================================

def getGitHubFileContent(
    owner: str,
    repository: str,
    path: str,
    branch: str | None = None,
) -> str:

    if branch is None:

        repositoryInfo = (
            getGitHubRepository(
                owner=owner,
                repository=repository,
            )
        )

        branch = (
            repositoryInfo.get(
                "default_branch",
                "main",
            )
        )

    url = (
        "https://raw.githubusercontent.com/"
        f"{owner}/{repository}/"
        f"{quote(branch, safe='')}/"
        f"{quote(path, safe='')}"
    )

    response = requests.get(
        url,
        headers=getGitHubHeaders(),
        timeout=30,
    )

    response.raise_for_status()

    return response.text


# ============================================================
# Select useful technical files
# ============================================================

def selectTechnicalFiles(
    paths: list[str],
    maxFiles: int = 8,
) -> list[str]:
    """
    Select repository files that are likely to contain
    useful technical information.

    We deliberately avoid reading every file because a
    repository may contain thousands of files.
    """

    priorityFiles = []

    secondaryFiles = []

    for path in paths:

        normalized = path.lower()

        filename = (
            normalized.split("/")[-1]
        )

        # =================================================
        # HIGH PRIORITY
        # =================================================

        if filename in {
            "readme.md",
            "readme.rst",
            "readme.txt",
            "requirements.txt",
            "pyproject.toml",
            "setup.py",
            "setup.cfg",
            "dockerfile",
        }:

            priorityFiles.append(
                path
            )

            continue

        # =================================================
        # DOCUMENTATION
        # =================================================

        if (
            "docs/" in normalized
            or normalized.startswith("docs")
        ):

            if filename.endswith(
                (
                    ".md",
                    ".rst",
                    ".txt",
                )
            ):

                secondaryFiles.append(
                    path
                )

                continue

        # =================================================
        # TRAINING / FINE-TUNING
        # =================================================

        trainingKeywords = {
            "train",
            "training",
            "finetune",
            "fine_tune",
            "fine-tune",
            "lora",
            "peft",
        }

        if any(
            keyword in normalized
            for keyword in trainingKeywords
        ):

            if filename.endswith(
                (
                    ".py",
                    ".md",
                    ".yaml",
                    ".yml",
                    ".json",
                    ".toml",
                )
            ):

                secondaryFiles.append(
                    path
                )

                continue

        # =================================================
        # INFERENCE
        # =================================================

        inferenceKeywords = {
            "infer",
            "inference",
            "predict",
            "transcribe",
            "decode",
            "serve",
            "serving",
        }

        if any(
            keyword in normalized
            for keyword in inferenceKeywords
        ):

            if filename.endswith(
                (
                    ".py",
                    ".md",
                    ".yaml",
                    ".yml",
                    ".json",
                    ".toml",
                )
            ):

                secondaryFiles.append(
                    path
                )

    selected = []

    # =================================================
    # PRIORITY FILES FIRST
    # =================================================

    for path in priorityFiles:

        if path not in selected:

            selected.append(
                path
            )

        if len(selected) >= maxFiles:
            return selected

    # =================================================
    # SECONDARY FILES
    # =================================================

    for path in secondaryFiles:

        if path not in selected:

            selected.append(
                path
            )

        if len(selected) >= maxFiles:
            break

    return selected


# ============================================================
# Technical repository research
# ============================================================

def getGitHubTechnicalEvidence(
    query: str,
    limit: int = 5,
    maxRepositories: int = 3,
    maxFilesPerRepository: int = 8,
    maxCharactersPerFile: int = 15000,
) -> list[dict]:
    """
    Search GitHub for repositories and inspect a small
    number of relevant files from the best repositories.

    This provides technical evidence rather than only
    repository metadata.
    """

    repositories = searchGitHubRepositories(
        query=query,
        limit=limit,
    )

    evidence = []

    # =================================================
    # INSPECT TOP REPOSITORIES
    # =================================================

    for repo in repositories[
        :maxRepositories
    ]:

        repositoryFullName = repo.get(
            "metadata",
            {},
        ).get(
            "repositoryId"
        )

        if not repositoryFullName:
            continue

        if "/" not in repositoryFullName:
            continue

        owner, repository = (
            repositoryFullName.split(
                "/",
                1,
            )
        )

        # =================================================
        # REPOSITORY METADATA
        # =================================================

        try:

            repositoryInfo = (
                getGitHubRepository(
                    owner=owner,
                    repository=repository,
                )
            )

        except Exception as error:

            print(
                "Failed to inspect GitHub "
                f"repository {repositoryFullName}:"
            )

            print(error)

            continue

        branch = (
            repositoryInfo.get(
                "default_branch",
                "main",
            )
        )

        # Add repository metadata as evidence.

        evidence.append(
            {
                **repo,

                "metadata": {
                    **repo.get(
                        "metadata",
                        {},
                    ),

                    "repositoryId": (
                        repositoryFullName
                    ),

                    "defaultBranch": branch,

                    "homepage": (
                        repositoryInfo.get(
                            "homepage"
                        )
                    ),

                    "license": (
                        (
                            repositoryInfo.get(
                                "license"
                            ) or {}
                        ).get(
                            "spdx_id"
                        )
                    ),

                    "topics": (
                        repositoryInfo.get(
                            "topics",
                            [],
                        )
                    ),
                },
            }
        )

        # =================================================
        # FILE TREE
        # =================================================

        try:

            paths = (
                getGitHubRepositoryFiles(
                    owner=owner,
                    repository=repository,
                    branch=branch,
                )
            )

        except Exception as error:

            print(
                "Failed to retrieve GitHub "
                f"file tree for {repositoryFullName}:"
            )

            print(error)

            continue

        selectedFiles = (
            selectTechnicalFiles(
                paths,
                maxFiles=maxFilesPerRepository,
            )
        )

        # =================================================
        # READ SELECTED FILES
        # =================================================

        for path in selectedFiles:

            try:

                content = (
                    getGitHubFileContent(
                        owner=owner,
                        repository=repository,
                        path=path,
                        branch=branch,
                    )
                )

                content = content[
                    :maxCharactersPerFile
                ]

                fileUrl = (
                    f"https://github.com/"
                    f"{owner}/{repository}/blob/"
                    f"{quote(branch, safe='')}/"
                    f"{quote(path, safe='')}"
                )

                evidence.append(
                    {
                        "source": "github",

                        "title": (
                            f"{repositoryFullName}"
                            f" / {path}"
                        ),

                        "url": fileUrl,

                        "description": (
                            "Technical file from "
                            "a GitHub repository."
                        ),

                        "metadata": {

                            "repositoryId": (
                                repositoryFullName
                            ),

                            "filePath": path,

                            "branch": branch,

                            "content": content,
                        },
                    }
                )

            except Exception as error:

                if (
                    path.lower()
                    .endswith(
                        (
                            ".md",
                            ".rst",
                            ".txt",
                        )
                    )
                ):

                    print(
                        "Failed to retrieve GitHub "
                        f"file {repositoryFullName}/{path}:"
                    )

                    print(error)

    return evidence