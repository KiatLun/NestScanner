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

response = client.chat.completions.create(
    model=os.getenv("OPENAI_MODEL"),
    messages=[
        {"role": "user", "content": "how to make a cup of tea?"},
    ],
)

print("\nResponse:")
print(response.choices[0].message.content)