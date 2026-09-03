import json

from app.graph.workflow import (
    build_graph,
)

from app.database.db import (
    initializeDatabase,
    createScan,
    completeScan,
)


def main():

    # =================================================
    # 1. INITIALIZE DATABASE
    # =================================================

    initializeDatabase()

    # =================================================
    # 2. CREATE SCAN
    # =================================================

    query = "Find automatic speech recognition " "models from recent sources."

    scanId = createScan(query)

    print(f"\nCreated scan: " f"{scanId}")

    # =================================================
    # 3. BUILD GRAPH
    # =================================================

    graph = build_graph()

    initialState = {
        "query": query,
        "scanId": scanId,
    }

    # =================================================
    # 4. RUN GRAPH
    # =================================================

    result = graph.invoke(initialState)

    # =================================================
    # 5. COMPLETE RUN
    # =================================================

    completeScan(scanId)

    print("\n=== FINAL GRAPH RESULT ===")

    print(
        json.dumps(
            result,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
