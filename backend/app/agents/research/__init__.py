import json
import re

from pathlib import Path

from app.models.state import ScanState

from app.agents.research.agent import (
    researchAgent,
)

from app.agents.research.config import (
    defaultResearchConfig,
)


def makeSafeFilename(
    name: str,
) -> str:

    safeName = re.sub(
        r'[<>:"/\\|?*]',
        "_",
        name,
    )

    return safeName.strip() or "unknown_model"


def research_agent(
    state: ScanState,
) -> dict:

    researchConfig = defaultResearchConfig

    candidates = state.get(
        "candidates",
        [],
    )

    runOutputPath = state.get("runOutputPath")

    researchResults = []

    researchFolder = None

    if runOutputPath:

        researchFolder = Path(runOutputPath) / "research"

        researchFolder.mkdir(
            parents=True,
            exist_ok=True,
        )

    for index, researchInput in enumerate(
        candidates,
        start=1,
    ):

        result = researchAgent(
            researchInput,
            researchConfig,
        )

        researchResults.append(result)

        if researchFolder:

            candidate = researchInput.get(
                "candidate",
                {},
            )

            modelName = candidate.get(
                "name",
                f"candidate_{index}",
            )

            safeName = makeSafeFilename(modelName)

            outputPath = researchFolder / f"{index:02d}_{safeName}.json"

            with open(
                outputPath,
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    result,
                    file,
                    indent=2,
                    ensure_ascii=False,
                )

    return {"researchResults": researchResults}
