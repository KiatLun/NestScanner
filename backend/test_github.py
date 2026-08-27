import json

from app.tools.github import searchGitHubRepositories


def main():

    print("\n=== TEST GITHUB SEARCH ===")

    results = searchGitHubRepositories(
        "automatic speech recognition ASR",
        limit=30,
    )

    print(f"\nFound {len(results)} repositories.\n")

    print(
        json.dumps(
            results,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
