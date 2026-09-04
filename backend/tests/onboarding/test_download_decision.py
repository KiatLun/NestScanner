import json

from app.services.echoforge.downloadSourceResolver import (
    resolveDownloadSource,
)

from app.services.echoforge.modelInfoReader import (
    getAllModelInfo,
)

from app.services.echoforge.downloaderResolver import (
    resolveDownloader,
)

EXPECTED_RESULTS = {
    "Qwen3-ASR-1.7B": {
        "sourceType": "huggingface",
        "source": "Qwen/Qwen3-ASR-1.7B",
        "downloader": "hugging_face_download",
        "scope": "generic",
    },
    "Voxtral-Mini-3B-2507": {
        "sourceType": "huggingface",
        "source": "mistralai/Voxtral-Mini-3B-2507",
        "downloader": "voxtral_download",
        "scope": "model-specific",
    },
    "Whisper Medium": {
        "sourceType": "huggingface",
        "source": "openai/whisper-medium",
        "downloader": "whisper_download",
        "scope": "model-specific",
    },
    "Silero VAD": {
        "sourceType": "github",
        "source": "https://github.com/snakers4/silero-vad",
        "downloader": "silero_download",
        "scope": "model-specific",
    },
    "Mega-ASR": {
        "sourceType": "huggingface",
        "source": "zhifeixie/Mega-ASR",
        "downloader": "hugging_face_download",
        "scope": "generic",
    },
    "Example Direct ASR": {
        "sourceType": "directUrl",
        "source": ("https://example.org/models/" "example-asr/model.bin"),
        "downloader": None,
        "scope": None,
    },
}


def main():

    with open(
        "tests/onboarding/sampleOutput.json",
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    researchResults = data["research"]["results"]

    modelInfo = getAllModelInfo()

    passed = 0
    failed = 0

    print()
    print("=" * 80)
    print("END-TO-END DOWNLOAD DECISION TEST")
    print("=" * 80)

    for researchResult in researchResults:

        modelName = researchResult["candidate"]["name"]

        expected = EXPECTED_RESULTS.get(modelName)

        if not expected:
            print()
            print(f"[SKIP] {modelName}")
            continue

        print()
        print("-" * 80)
        print(f"Testing: {modelName}")
        print("-" * 80)

        # Step 1:
        # determine where model should be downloaded from
        try:
            sourceResult = resolveDownloadSource(researchResult)

        except Exception as error:
            failed += 1

            print("[FAIL] Source resolution error")
            print(f"       {error}")

            continue

        sourceType = sourceResult["sourceType"]

        source = sourceResult["source"]

        print()
        print("Resolved source:")
        print(f"  sourceType: {sourceType}")
        print(f"  source:     {source}")

        # Step 2:
        # determine whether echoforge already
        # has a downloader that can handle it
        downloaderResult = resolveDownloader(
            modelName=modelName,
            sourceType=sourceType,
            source=source,
            modelInfo=modelInfo,
        )

        if downloaderResult:

            actualDownloader = downloaderResult.get("downloader")

            actualScope = downloaderResult.get("scope")

        else:

            actualDownloader = None
            actualScope = None

        print()
        print("Resolved downloader:")
        print(f"  downloader: {actualDownloader}")
        print(f"  scope:      {actualScope}")

        actual = {
            "sourceType": sourceType,
            "source": source,
            "downloader": actualDownloader,
            "scope": actualScope,
        }

        fieldsToCompare = [
            "sourceType",
            "source",
            "downloader",
            "scope",
        ]

        testPassed = True

        print()
        print("Field comparison:")

        for field in fieldsToCompare:

            expectedValue = expected.get(field)

            actualValue = actual.get(field)

            if actualValue == expectedValue:

                print(f"[PASS] {field}")

                print(f"       {actualValue}")

            else:

                testPassed = False

                print(f"[FAIL] {field}")

                print(f"       Expected: " f"{expectedValue}")

                print(f"       Actual:   " f"{actualValue}")

        if testPassed:

            passed += 1

            print()
            print(f"[RESULT] PASS - " f"{modelName}")

        else:

            failed += 1

            print()
            print(f"[RESULT] FAIL - " f"{modelName}")

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    print(f"Passed: {passed}")

    print(f"Failed: {failed}")

    print(f"Total:  {passed + failed}")

    print("=" * 80)


if __name__ == "__main__":
    main()
