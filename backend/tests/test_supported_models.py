from app.services.echoforge.modelInfoReader import (
    getAllSupportedModels,
)


def main():
    models = getAllSupportedModels()

    print(f"Found {len(models)} supported models.")

    for model in models:
        print()
        print(f"Source: {model['source']}")
        print(f"Cache: {model['cacheName']}")
        print(f"Downloader: {model['downloader']}")
        print(f"Scope: {model['scope']}")
        print(f"Source Type: {model['sourceType']}")


if __name__ == "__main__":
    main()
