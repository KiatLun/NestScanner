import json

from tools.arvixSearch import (
    search_arxiv_papers,
)


def main():

    results = search_arxiv_papers(
        "automatic speech recognition",
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
