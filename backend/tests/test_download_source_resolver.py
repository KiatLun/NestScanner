import json

from app.services.echoforge.downloadSourceResolver import (
    resolveDownloadSource,
)


def main():

    with open(
        "app/agents/research/sampleOutput.json",
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    researchResults = data["research"]["results"]

    megaAsr = None

    for result in researchResults:

        candidate = result.get(
            "candidate",
            {},
        )

        if candidate.get("name") == "Mega-ASR":

            megaAsr = result
            break

    if not megaAsr:

        raise RuntimeError("Mega-ASR research result not found.")

    result = resolveDownloadSource(megaAsr)

    print(
        json.dumps(
            result,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
