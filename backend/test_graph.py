import json

from app.graph.workflow import (
    build_graph,
)

from app.database.db import (
    initializeDatabase,
    createScanRun,
    completeScanRun,
)


def main():

    # =================================================
    # 1. INITIALIZE DATABASE
    # =================================================

    initializeDatabase()

    # =================================================
    # 2. CREATE SCAN RUN
    # =================================================

    query = "Find automatic speech recognition " "models from recent sources."

    runId = createScanRun(query)

    print(f"\nCreated scan run: " f"{runId}")

    # =================================================
    # 3. BUILD GRAPH
    # =================================================

    graph = build_graph()

    initialState = {
        "query": query,
        "runId": runId,
    }

    # =================================================
    # 4. RUN GRAPH
    # =================================================

    result = graph.invoke(initialState)

    # =================================================
    # 5. COMPLETE RUN
    # =================================================

    completeScanRun(runId)

    print("\n=== FINAL GRAPH RESULT ===")

    print(
        json.dumps(
            result,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
