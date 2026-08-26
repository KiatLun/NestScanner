import os
from dotenv import load_dotenv

load_dotenv()

LAB_LLM_API_KEY = os.getenv("LAB_LLM_API_KEY")

LAB_LLM_BASE_URL = os.getenv(
    "LAB_LLM_BASE_URL",
    "https://llm-api.nestlab.sg/v1",
)

LAB_LLM_MODEL = os.getenv(
    "LAB_LLM_MODEL",
    "qwen3.8-27b",
)

MAX_RESEARCH_RETRIES = 3


if not LAB_LLM_API_KEY:
    raise RuntimeError(
        "LAB_LLM_API_KEY is missing. "
        "Add it to your .env file."
    )