from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.services.llm_service import ask_llm
from app.services.huggingface_service import get_asr_models
from app.agents.discovery_agent import discover_asr_models

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Backend is running"}

@app.get("/api/test-llm")
def test_llm():
    response = ask_llm("return \"LLM Connection Successful\" if the LLM is working properly.")

    return {
        "response": response
    }

@app.get("/api/huggingface/asr-models")
def get_asr_models_endpoint():
    models = get_asr_models(limit=20)
    return {"models": models}

@app.get("/api/discover")
def discover_asr_models_endpoint():
    response = discover_asr_models(limit=20)
    return {"result": response}