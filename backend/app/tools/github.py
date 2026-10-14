import os

import requests
from dotenv import load_dotenv
from urllib.parse import quote


load_dotenv()


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


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
                "title": (
                    repo.get(
                        "full_name"
                    )
                ),
                "url": (
                    repo.get(
                        "html_url"
                    )
                ),
                "description": (
                    repo.get(
                        "description"
                    )
                ),
                "metadata": {
                    "stars": (
                        repo.get(
                            "stargazers_count"
                        )
                    ),
                    "language": (
                        repo.get(
                            "language"
                        )
                    ),
                    "createdAt": (
                        repo.get(
                            "created_at"
                        )
                    ),
                    "updatedAt": (
                        repo.get(
                            "updated_at"
                        )
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
        f"{quote(branch)}"
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
        f"{branch}/{path}"
    )

    response = requests.get(
        url,
        headers=getGitHubHeaders(),
        timeout=30,
    )

    response.raise_for_status()

    return response.text