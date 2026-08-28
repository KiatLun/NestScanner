from app.services.echoforge.modelDownloader import (
    downloadHuggingFaceModel,
)


def main():

    result = downloadHuggingFaceModel(
        repoId="openai/whisper-tiny",
        cacheName="nestscanner-service-test",
    )

    print("\n=== DOWNLOAD RESULT ===")

    print(result)


if __name__ == "__main__":
    main()
