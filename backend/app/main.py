import json

from fastapi import (
    FastAPI,
    HTTPException,
)
from fastapi.middleware.cors import CORSMiddleware
from app.database.db import (
    getAllScans,
    getScan,
    getLatestScan,
)
from app.agents.discovery import discoveryAgent
from app.agents.research.agent import researchAgent
from app.llm.client import getLLM
from app.tools.huggingFace import searchHuggingFaceModels

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
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
    return {"message": "Backend is running"}


# =====================================================
# TEST LLM
# =====================================================


@app.get("/api/test-llm")
def testLlm():

    llm = getLLM()

    response = llm.invoke("""
Return the current date in YYYY-MM-DD format.

Also return:
"LLM Connection Successful"
""")

    return {"response": response.content}


# =====================================================
# TEST HUGGING FACE
# =====================================================


@app.get("/api/huggingface/asr-models")
def getAsrModels():

    models = searchHuggingFaceModels(
        query="speech recognition",
        limit=20,
    )

    return {"models": models}


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

    result = discoveryAgent(state)

    return {"result": result}


# =====================================================
# TEMP RESEARCH TEST
# =====================================================


@app.get("/api/test-research")
def testResearch(
    candidateIndex: int = 0,
):

    with open(
        "app/agents/discovery/sampleOutput.txt",
        "r",
        encoding="utf-8",
    ) as file:
        discoveryOutput = json.load(file)

    candidates = discoveryOutput.get(
        "candidates",
        [],
    )

    if candidateIndex < 0 or candidateIndex >= len(candidates):
        return {"error": "Invalid candidateIndex"}

    researchInput = candidates[candidateIndex]

    result = researchAgent(researchInput)

    return {"result": result}


@app.get("/api/getAllScans")
def getAllScansEndpoint():

    scans = getAllScans()

    return {
        "scans": scans,
    }


@app.get("/api/getScan/{scanId}")
def getScanEndpoint(
    scanId: int,
):

    scan = getScan(scanId)

    if scan is None:
        raise HTTPException(
            status_code=404,
            detail=(f"Scan {scanId} " "not found"),
        )

    return scan


@app.get("/api/getLatestScan")
def getLatestScanEndpoint():

    scan = getLatestScan()

    if scan is None:
        raise HTTPException(
            status_code=404,
            detail=("No scans found"),
        )

    return scan
