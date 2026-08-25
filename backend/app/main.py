from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agents.discovery import discoveryAgent
from app.llm.client import getLLM
from app.tools.huggingFace import searchHuggingFaceModels


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


# =====================================================
# ROOT
# =====================================================


@app.get("/")
def root():
    return {
        "message": "Backend is running"
    }


# =====================================================
# TEST LLM
# =====================================================


@app.get("/api/test-llm")
def testLlm():

    llm = getLLM()

    response = llm.invoke(
        """
Return the current date in YYYY-MM-DD format.

Also return:
"LLM Connection Successful"
"""
    )

    return {
        "response": response.content
    }


# =====================================================
# TEST HUGGING FACE
# =====================================================


@app.get("/api/huggingface/asr-models")
def getAsrModels():

    models = searchHuggingFaceModels(
        query="speech recognition",
        limit=20,
    )

    return {
        "models": models
    }


# =====================================================
# DISCOVERY
# =====================================================


@app.get("/api/discover")
def discoverAsrModels():

    state = {
        "query": (
            "Find automatic speech recognition "
            "models released within the past 30 days."
        )
    }

    result = discoveryAgent(
        state
    )

    return {
        "result": result
    }