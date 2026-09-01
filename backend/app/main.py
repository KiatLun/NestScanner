import json

from dataclasses import asdict
from fastapi import (
    FastAPI,
    HTTPException,
    BackgroundTasks,
)

from fastapi.middleware.cors import (
    CORSMiddleware,
)

from pydantic import BaseModel

from app.database.db import (
    initializeDatabase,
    createScan,
    completeScan,
    failScan,
    getScanStatus,
    getAllScans,
    getScan,
    getLatestScan,
    getResearchByScan,
    getAllModels,
    getModel,
    getModelDetails,
)

from app.graph.workflow import (
    build_graph,
)

from app.agents.discovery import (
    discoveryAgent,
)

from app.agents.discovery.config import (
    DiscoveryConfig,
    defaultDiscoveryConfig,
)

from app.agents.research.agent import (
    researchAgent,
)

from app.agents.research.config import (
    ResearchConfig,
    defaultResearchConfig,
)

from app.llm.client import (
    getLLM,
)

from app.tools.huggingFace import (
    searchHuggingFaceModels,
)

app = FastAPI()

# =====================================================
# CORS
# =====================================================

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
# REQUEST SCHEMAS
# =====================================================


class StartScanRequest(BaseModel):

    query: str = "Find automatic speech recognition " "models from recent sources."

    discoveryConfig: dict | None = None

    researchConfig: dict | None = None


def runScan(
    scanId: int,
    query: str,
    discoveryConfig: dict,
    researchConfig: dict,
):

    try:

        graph = build_graph()

        initialState = {
            "query": query,
            "scanId": scanId,
            "discoveryConfig": (discoveryConfig),
            "researchConfig": (researchConfig),
        }

        graph.invoke(initialState)

        completeScan(scanId)

    except Exception as error:

        failScan(
            scanId,
            str(error),
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
# TEMP DISCOVERY TEST
# =====================================================


@app.get("/api/discover")
def discoverAsrModels():

    state = {
        "query": (
            "Find automatic speech recognition "
            "models released within the past "
            "30 days."
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

        raise HTTPException(
            status_code=400,
            detail=("Invalid candidateIndex"),
        )

    researchInput = candidates[candidateIndex]

    result = researchAgent(researchInput)

    return {"result": result}


# =====================================================
# START SCAN
# =====================================================


@app.post("/api/startScan")
def startScan(
    request: StartScanRequest,
    backgroundTasks: BackgroundTasks,
):

    # =================================================
    # 1. RESOLVE DISCOVERY CONFIG
    # =================================================

    try:

        if request.discoveryConfig:

            discoveryConfig = DiscoveryConfig(**request.discoveryConfig)

        else:

            discoveryConfig = defaultDiscoveryConfig

    except TypeError as error:

        raise HTTPException(
            status_code=400,
            detail=("Invalid Discovery config: " f"{error}"),
        )

    # =================================================
    # 2. RESOLVE RESEARCH CONFIG
    # =================================================

    try:

        if request.researchConfig:

            researchConfig = ResearchConfig(**request.researchConfig)

        else:

            researchConfig = defaultResearchConfig

    except TypeError as error:

        raise HTTPException(
            status_code=400,
            detail=("Invalid Research config: " f"{error}"),
        )

    # =================================================
    # 3. CONVERT CONFIGS
    # =================================================

    discoveryConfigUsed = asdict(discoveryConfig)

    researchConfigUsed = asdict(researchConfig)

    # =================================================
    # 4. INITIALIZE DATABASE
    # =================================================

    initializeDatabase()

    # =================================================
    # 5. CREATE SCAN
    # =================================================

    scanId = createScan(
        request.query,
        discoveryConfigUsed,
        researchConfigUsed,
    )

    # =================================================
    # 6. START BACKGROUND SCAN
    # =================================================

    backgroundTasks.add_task(
        runScan,
        scanId,
        request.query,
        discoveryConfigUsed,
        researchConfigUsed,
    )

    # =================================================
    # 7. RETURN IMMEDIATELY
    # =================================================

    return {
        "scanId": scanId,
        "query": request.query,
        "status": "running",
        "stage": "discovery",
        "discoveryConfig": (discoveryConfigUsed),
        "researchConfig": (researchConfigUsed),
    }


# =====================================================
# GET ALL SCANS
# =====================================================


@app.get("/api/getAllScans")
def getAllScansEndpoint():

    scans = getAllScans()

    return {
        "scans": scans,
    }


# =====================================================
# GET SCAN
# =====================================================


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


# =====================================================
# GET LATEST SCAN
# =====================================================


@app.get("/api/getLatestScan")
def getLatestScanEndpoint():

    scan = getLatestScan()

    if scan is None:

        raise HTTPException(
            status_code=404,
            detail=("No scans found"),
        )

    return scan


# =====================================================
# GET RESEARCH BY SCAN
# =====================================================


@app.get("/api/getResearchByScan/{scanId}")
def getResearchEndpoint(
    scanId: int,
):

    research = getResearchByScan(scanId)

    if research is None:

        raise HTTPException(
            status_code=404,
            detail=(f"Scan {scanId} " "not found"),
        )

    return research


@app.get("/api/getScanStatus/{scanId}")
def getScanStatusEndpoint(
    scanId: int,
):

    status = getScanStatus(scanId)

    if status is None:

        raise HTTPException(
            status_code=404,
            detail=(f"Scan {scanId} " "not found"),
        )

    return status


# =====================================================
# GET ALL MODELS
# =====================================================

@app.get("/api/getAllModels")
def getAllModelsEndpoint():
    
    models = getAllModels()

    return {"models": models}

# =====================================================
# GET MODEL
# =====================================================

@app.get("/api/getModel/{modelId}")
def getModelEndpoint(
    modelId: int,
):

    model = getModel(modelId)

    if model is None:

        raise HTTPException(
            status_code=404,
            detail=(f"Model {modelId} " "not found"),
        )

    return model

@app.get("/api/getModelDetails/{modelId}")
def getModelDetailsEndpoint(
    modelId: int,
):

    modelDetails = getModelDetails(modelId)

    if modelDetails is None:

        raise HTTPException(
            status_code=404,
            detail=(f"Model {modelId} " "not found"),
        )

    return modelDetails