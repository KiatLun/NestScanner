import json

from app.tools.webSearch import webSearch


def main():
    results = webSearch(
        "open source ASR speech recognition model 2026",
        maxResults=5,
    )

    print(
        json.dumps(
            results,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
