from app.services.echoforge.modelUploader import (
    uploadModel,
)


def main():

    result = uploadModel(
        cacheName="nestscanner-test-whisper",
        modelName="nestscanner-test-whisper",
    )

    print("\n=== UPLOAD RESULT ===")

    print(result)


if __name__ == "__main__":
    main()
