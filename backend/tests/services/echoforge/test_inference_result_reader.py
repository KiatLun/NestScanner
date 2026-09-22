from pprint import pprint

from app.services.echoforge.inferenceResultReader import (
    getInferenceResult,
)


TASK_ID = (
    "564b2937681f4130a8bebadebdc412da"
)


def main():

    result = getInferenceResult(
        TASK_ID
    )

    print()
    print(
        "=" * 60
    )
    print(
        "INFERENCE RESULT"
    )
    print(
        "=" * 60
    )

    pprint(
        result,
        sort_dicts=False,
    )


if __name__ == "__main__":
    main()