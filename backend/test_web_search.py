import json

from tools.webSearch import webSearch


def main():
    results = webSearch(
        "open source ASR speech recognition model 2026",
        max_results=5,
    )

    print(
        json.dumps(
            results,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
