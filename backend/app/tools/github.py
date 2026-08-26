import requests

GITHUB_SEARCH_URL = "https://api.github.com/search/repositories"


def searchGithubRepositories(
    query: str,
    limit: int = 10,
) -> list[dict]:

    params = {
        "q": query,
        "sort": "updated",
        "order": "desc",
        "per_page": limit,
    }

    response = requests.get(
        GITHUB_SEARCH_URL,
        params=params,
        timeout=15,
    )

    response.raise_for_status()

    data = response.json()

    results = []

    for repo in data.get("items", []):

        results.append(
            {
                "source": "github",
                "title": repo.get("full_name"),
                "url": repo.get("html_url"),
                "description": repo.get("description"),
                "metadata": {
                    "organisation": (repo.get("owner", {}).get("login")),
                    "stars": repo.get("stargazers_count"),
                    "forks": repo.get("forks_count"),
                    "language": repo.get("language"),
                    "updated_at": repo.get("updated_at"),
                    "topics": repo.get("topics", []),
                },
            }
        )

    return results
