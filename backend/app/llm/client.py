from langchain_openai import ChatOpenAI

from app.config.settings import (
    LAB_LLM_API_KEY,
    LAB_LLM_BASE_URL,
    LAB_LLM_MODEL,
)


def getLLM() -> ChatOpenAI:
    return ChatOpenAI(
        model=LAB_LLM_MODEL,
        base_url=LAB_LLM_BASE_URL,
        api_key=LAB_LLM_API_KEY,
        temperature=0,
    )
