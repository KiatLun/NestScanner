import json

from app.graph.workflow import build_graph


def main():

    graph = build_graph()

    initialState = {
        "query": (
            "Find automatic speech recognition "
            "models from recent sources."
        )
    }

    result = graph.invoke(
        initialState
    )

    print(
        "\n=== FINAL GRAPH RESULT ==="
    )

    print(
        json.dumps(
            result,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()