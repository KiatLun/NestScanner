import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

print("Base URL:", os.getenv("OPENAI_BASE_URL"))
print("Model:", os.getenv("OPENAI_MODEL"))
print("API key loaded:", bool(os.getenv("OPENAI_API_KEY")))

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

def ask_llm(prompt: str):
    response = client.chat.completions.create(
        model = os.getenv("OPENAI_MODEL"),
        messages = [
            {"role": "user", "content": prompt}
        ],
    )
    return response.choices[0].message.content

response = ask_llm("what day is today?")
