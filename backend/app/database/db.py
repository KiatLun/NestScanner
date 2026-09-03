import json
import sqlite3

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

DATABASE_PATH = Path("data") / "nestScanner.db"


def getConnection():
    """
    Create and return a connection to the NestScanner
    SQLite database.
    """

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(DATABASE_PATH)

    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initializeDatabase():
    """
    Create database tables if they do not already exist.
    """

    connection = getConnection()

    cursor = connection.cursor()

    # =================================================
    # SCANS
    # =================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        query TEXT NOT NULL,

        discovery_config TEXT,
        research_config TEXT,

        status TEXT NOT NULL DEFAULT 'running',
        stage TEXT,
        error TEXT,

        started_at TEXT NOT NULL,
        completed_at TEXT
    )
    """)

    # =================================================
    # MODELS
    # =================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,
            organisation TEXT,
            source_url TEXT,
            candidate_type TEXT,
            UNIQUE(name, source_url)
        )
    """)

    # =================================================
    # SCAN MODELS
    # =================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            scan_id INTEGER NOT NULL,
            model_id INTEGER NOT NULL,

            discovery_evidence TEXT,

            FOREIGN KEY (scan_id)
                REFERENCES scans(id)
                ON DELETE CASCADE,

            FOREIGN KEY (model_id)
                REFERENCES models(id)
                ON DELETE CASCADE,

            UNIQUE(scan_id, model_id)
        )
    """)

    # =================================================
    # RESEARCH RESULTS
    # =================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            scan_id INTEGER NOT NULL,
            model_id INTEGER NOT NULL,

            release_date TEXT,
            is_recent INTEGER,
            is_locally_deployable INTEGER,

            technical_profile TEXT,
            research_evidence TEXT,

            FOREIGN KEY (scan_id)
                REFERENCES scans(id)
                ON DELETE CASCADE,

            FOREIGN KEY (model_id)
                REFERENCES models(id)
                ON DELETE CASCADE,

            UNIQUE(scan_id, model_id)
        )
    """)

    connection.commit()

    connection.close()


def createScan(
    query: str,
    discoveryConfig: dict,
    researchConfig: dict,
) -> int:

    currentTime = datetime.now(ZoneInfo("Asia/Singapore")).isoformat()

    connection = getConnection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO scans (
            query,
            discovery_config,
            research_config,
            status,
            stage,
            started_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            query,
            json.dumps(
                discoveryConfig,
                ensure_ascii=False,
            ),
            json.dumps(
                researchConfig,
                ensure_ascii=False,
            ),
            "running",
            "discovery",
            currentTime,
        ),
    )

    scanId = cursor.lastrowid

    connection.commit()
    connection.close()

    return scanId


def completeScan(
    scanId: int,
):

    currentTime = datetime.now(ZoneInfo("Asia/Singapore")).isoformat()

    connection = getConnection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE scans
        SET
            status = ?,
            stage = ?,
            completed_at = ?
        WHERE id = ?
        """,
        (
            "completed",
            None,
            currentTime,
            scanId,
        ),
    )

    connection.commit()
    connection.close()


def updateScanStage(
    scanId: int,
    stage: str,
):

    connection = getConnection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE scans
        SET stage = ?
        WHERE id = ?
        """,
        (
            stage,
            scanId,
        ),
    )

    connection.commit()
    connection.close()


def failScan(
    scanId: int,
    error: str,
):

    currentTime = datetime.now(ZoneInfo("Asia/Singapore")).isoformat()

    connection = getConnection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE scans
        SET
            status = ?,
            error = ?,
            completed_at = ?
        WHERE id = ?
        """,
        (
            "failed",
            error,
            currentTime,
            scanId,
        ),
    )

    connection.commit()
    connection.close()


def getScanStatus(
    scanId: int,
) -> dict | None:

    connection = getConnection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            status,
            stage,
            error,
            started_at,
            completed_at
        FROM scans
        WHERE id = ?
        """,
        (scanId,),
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return {
        "scanId": row["id"],
        "status": row["status"],
        "stage": row["stage"],
        "error": row["error"],
        "startedAt": row["started_at"],
        "completedAt": row["completed_at"],
    }


def saveDiscoveryCandidate(
    scanId: int,
    discoveryCandidate: dict,
) -> int:
    """
    Save one discovered model.

    If the model already exists, reuse its model ID.

    A model is uniquely identified by:
        (name, source_url)

    Then associate the model with this scan.

    Returns the model ID.
    """

    candidate = discoveryCandidate["candidate"]

    name = candidate.get("name")
    sourceUrl = candidate.get("sourceUrl")

    discoveryEvidence = discoveryCandidate.get(
        "discoveryEvidence",
        [],
    )

    connection = getConnection()
    cursor = connection.cursor()

    # =================================================
    # CHECK IF MODEL ALREADY EXISTS
    # =================================================

    cursor.execute(
        """
        SELECT id
        FROM models
        WHERE name = ?
          AND source_url = ?
        """,
        (
            name,
            sourceUrl,
        ),
    )

    row = cursor.fetchone()

    # =================================================
    # CREATE MODEL IF IT DOES NOT EXIST
    # =================================================

    if row is None:

        cursor.execute(
            """
            INSERT INTO models (
                name,
                organisation,
                source_url,
                candidate_type
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                name,
                candidate.get("organisation"),
                sourceUrl,
                candidate.get("candidateType"),
            ),
        )

        modelId = cursor.lastrowid

    else:

        modelId = row["id"]

    # =================================================
    # LINK MODEL TO THIS SCAN
    # =================================================

    cursor.execute(
        """
        INSERT OR IGNORE INTO scan_models (
            scan_id,
            model_id,
            discovery_evidence
        )
        VALUES (?, ?, ?)
        """,
        (
            scanId,
            modelId,
            json.dumps(
                discoveryEvidence,
                ensure_ascii=False,
            ),
        ),
    )

    connection.commit()
    connection.close()

    return modelId

def saveResearchResult(
    scanId: int,
    modelId: int,
    result: dict,
) -> int:
    """
    Save one Research result for a model
    during a particular scan.

    Returns the database research result ID.
    """

    connection = getConnection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO research_results (
            scan_id,
            model_id,
            release_date,
            is_recent,
            is_locally_deployable,
            technical_profile,
            research_evidence
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            scanId,
            modelId,
            result.get("releaseDate"),
            result.get("isRecent"),
            result.get("isLocallyDeployable"),
            json.dumps(
                result.get("technicalProfile"),
                ensure_ascii=False,
            ),
            json.dumps(
                result.get(
                    "researchEvidence",
                    {},
                ),
                ensure_ascii=False,
            ),
        ),
    )

    researchResultId = cursor.lastrowid

    connection.commit()
    connection.close()

    return researchResultId


def getAllScans() -> list[dict]:
    """
    Return all scans, newest first.
    """

    connection = getConnection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            query,
            started_at,
            completed_at
        FROM scans
        ORDER BY id DESC
        """)

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


def getScan(
    scanId: int,
) -> dict | None:
    """
    Return one scan and its Discovery candidates.
    """

    connection = getConnection()

    cursor = connection.cursor()

    # =================================================
    # GET RUN
    # =================================================

    cursor.execute(
        """
        SELECT
            id,
            query,
            started_at,
            completed_at
        FROM scans
        WHERE id = ?
        """,
        (scanId,),
    )

    scanRow = cursor.fetchone()

    if scanRow is None:
        connection.close()
        return None

    # =================================================
    # GET DISCOVERY CANDIDATES
    # =================================================

    cursor.execute(
        """
        SELECT
            m.id AS model_id,
            m.name,
            m.organisation,
            m.source_url,
            m.candidate_type,
            sm.discovery_evidence

        FROM scan_models sm

        JOIN models m
            ON sm.model_id = m.id

        WHERE sm.scan_id = ?

        ORDER BY sm.id ASC
        """,
        (scanId,),
    )

    modelRows = cursor.fetchall()

    connection.close()

    models = []

    for row in modelRows:

        discoveryEvidence = []

        if row["discovery_evidence"]:
            try:
                discoveryEvidence = json.loads(
                    row["discovery_evidence"]
                )
            except json.JSONDecodeError:
                discoveryEvidence = []

        models.append(
            {
                "modelId": row["model_id"],
                "candidate": {
                    "name": row["name"],
                    "organisation": row["organisation"],
                    "sourceUrl": row["source_url"],
                    "candidateType": row["candidate_type"],
                },
                "discoveryEvidence": discoveryEvidence,
            }
        )

    return {
        "scan": dict(scanRow),
        "discovery": {
            "candidates": models,
        },
    }


def getLatestScan() -> dict | None:
    """
    Return the latest scan and its Discovery output.
    """

    connection = getConnection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT id
        FROM scans
        ORDER BY id DESC
        LIMIT 1
        """)

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return getScan(row["id"])


def getResearchByScan(
    scanId: int,
) -> dict | None:

    connection = getConnection()

    cursor = connection.cursor()

    # =================================================
    # CHECK SCAN EXISTS
    # =================================================

    cursor.execute(
        """
        SELECT
            id,
            query,
            started_at,
            completed_at
        FROM scans
        WHERE id = ?
        """,
        (scanId,),
    )

    scanRow = cursor.fetchone()

    if scanRow is None:
        connection.close()
        return None

    # =================================================
    # GET RESEARCH RESULTS
    # =================================================

    cursor.execute(
        """
        SELECT
            rr.id AS research_result_id,
            rr.model_id,
            rr.release_date,
            rr.is_recent,
            rr.is_locally_deployable,
            rr.technical_profile,
            rr.research_evidence,

            m.name,
            m.organisation,
            m.source_url,
            m.candidate_type

        FROM research_results rr

        JOIN models m
            ON rr.model_id = m.id

        WHERE rr.scan_id = ?

        ORDER BY rr.id ASC
        """,
        (scanId,),
    )

    rows = cursor.fetchall()

    connection.close()

    researchResults = []

    for row in rows:

        technicalProfile = None

        if row["technical_profile"]:
            try:
                technicalProfile = json.loads(row["technical_profile"])
            except json.JSONDecodeError:
                technicalProfile = None

        researchEvidence = {}

        if row["research_evidence"]:
            try:
                researchEvidence = json.loads(row["research_evidence"])
            except json.JSONDecodeError:
                researchEvidence = {}

        researchResults.append(
            {
                "researchResultId": row["research_result_id"],

                "modelId": row["model_id"],

                "candidate": {
                    "name": row["name"],
                    "organisation": row["organisation"],
                    "sourceUrl": row["source_url"],
                    "candidateType": row["candidate_type"],
                },

                "releaseDate": row["release_date"],

                "isRecent": (
                    None
                    if row["is_recent"] is None
                    else bool(row["is_recent"])
                ),

                "isLocallyDeployable": (
                    None
                    if row["is_locally_deployable"] is None
                    else bool(row["is_locally_deployable"])
                ),

                "technicalProfile": technicalProfile,

                "researchEvidence": researchEvidence,
            }
        )

    return {
        "scan": dict(scanRow),
        "research": {
            "results": researchResults,
        },
    }


def getAllModels() -> list[dict]:
    """
    Return all unique models in the models table, newest first.
    """

    connection = getConnection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            organisation,
            source_url,
            candidate_type
        FROM models
        ORDER BY id DESC
        """)

    rows = cursor.fetchall()

    connection.close()

    return [
        {
            "modelId": row["id"],
            "name": row["name"],
            "organisation": row["organisation"],
            "sourceUrl": row["source_url"],
            "candidateType": row["candidate_type"],
        }
         for row in rows
    ]


def getModel(
    modelId: int,
) -> dict | None:
    """
    Return one model by its ID.
    """

    connection = getConnection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            name,
            organisation,
            source_url,
            candidate_type
        FROM models
        WHERE id = ?
        """,
        (modelId,),
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return {
        "modelId": row["id"],
        "name": row["name"],
        "organisation": row["organisation"],
        "sourceUrl": row["source_url"],
        "candidateType": row["candidate_type"],
    }

def getModelDetails(
    modelId: int,
) -> dict | None:

    connection = getConnection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            m.id AS model_id,
            m.name,
            m.organisation,
            m.source_url,
            m.candidate_type,

            rr.id AS research_result_id,
            rr.scan_id,
            rr.release_date,
            rr.is_recent,
            rr.is_locally_deployable,
            rr.technical_profile,
            rr.research_evidence

        FROM models m

        LEFT JOIN research_results rr
            ON rr.id = (
                SELECT rr2.id
                FROM research_results rr2
                WHERE rr2.model_id = m.id
                ORDER BY rr2.id DESC
                LIMIT 1
            )

        WHERE m.id = ?
        """,
        (modelId,),
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None
    
    technicalProfile = None
    researchEvidence = {}

    if row["technical_profile"]:
        technicalProfile = json.loads(
            row["technical_profile"]
        )

    if row["research_evidence"]:
        researchEvidence = json.loads(
            row["research_evidence"]
        )
    return {
        "modelId": row["model_id"],
        "name": row["name"],
        "organisation": row["organisation"],
        "sourceUrl": row["source_url"],
        "candidateType": row["candidate_type"],

        "research": (
            None
            if row["research_result_id"] is None
            else {
                "researchResultId": row["research_result_id"],
                "scanId": row["scan_id"],
                "releaseDate": row["release_date"],
                "isRecent": (
                    None
                    if row["is_recent"] is None
                    else bool(row["is_recent"])
                ),
                "isLocallyDeployable": (
                    None
                    if row["is_locally_deployable"] is None
                    else bool(row["is_locally_deployable"])
                ),
                "technicalProfile": technicalProfile,
                "researchEvidence": researchEvidence,
            }
        ),
    }