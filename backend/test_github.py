import json

from tools.github import searchGithubRepositories


def main():
    results = searchGithubRepositories(
        "automatic speech recognition ASR",
        limit=5,
    )

    print(
        json.dumps(
            results,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
