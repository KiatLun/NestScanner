import os

import requests
from dotenv import load_dotenv

load_dotenv()


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def searchGitHubRepositories(
    query: str,
    limit: int = 10,
) -> list[dict]:

    url = "https://api.github.com/" "search/repositories"

    headers = {
        "Accept": ("application/vnd.github+json"),
    }

    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    params = {
        "q": query,
        "per_page": limit,
        "sort": "updated",
        "order": "desc",
    }

    response = requests.get(
        url,
        headers=headers,
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
                "title": repo.get("full_name"),
                "url": repo.get("html_url"),
                "description": repo.get("description"),
                "metadata": {
                    "stars": repo.get("stargazers_count"),
                    "language": repo.get("language"),
                    "createdAt": repo.get("created_at"),
                    "updatedAt": repo.get("updated_at"),
                },
            }
        )

    return results
