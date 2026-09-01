from app.services.echoforge.echoforgeClient import (
    getDownloaderCapabilities,
)
from app.services.echoforge.downloadResolver import (
    resolveDownloader,
)


def main():
    # NestScanner queries Echoforge on what downloaders are available for a given model and source type. It first fetches the capabilities from Echoforge, then resolves the appropriate downloader based on the model name and source type.
    capabilities = getDownloaderCapabilities()

    result = resolveDownloader(
        modelName="nemotron-speech-streaming-en-0.6b",
        sourceType="huggingface",
        capabilities=capabilities,
    )

    print(result)


if __name__ == "__main__":
    main()
