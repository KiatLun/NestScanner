import json

from app.tools.huggingFace import (
    searchHuggingFaceModels,
    filterASRModels,
)


def main():
    results = searchHuggingFaceModels(
        "speech recognition",
        limit=20,
    )

    asr_results = filterASRModels(results)
    print(
        json.dumps(
            asr_results,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
