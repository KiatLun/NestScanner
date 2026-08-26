from app.llm.client import getLLM


def main():
    llm = getLLM()

    response = llm.invoke("Reply with exactly: connection successful")

    print(response.content)


if __name__ == "__main__":
    main()
