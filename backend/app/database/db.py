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
            started_at TEXT NOT NULL,
            completed_at TEXT
        )
        """)

    # =================================================
    # DISCOVERY CANDIDATES
    # =================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS discovery_candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,

            name TEXT NOT NULL,
            organisation TEXT,
            source_url TEXT,
            candidate_type TEXT,

            discovery_evidence TEXT,

            FOREIGN KEY (run_id)
                REFERENCES scans(id)
                ON DELETE CASCADE
        )
        """)

    # =================================================
    # RESEARCH RESULTS
    # =================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            candidate_id INTEGER NOT NULL,

            release_date TEXT,
            is_recent INTEGER,
            is_locally_deployable INTEGER,

            technical_profile TEXT,
            research_evidence TEXT,

            FOREIGN KEY (run_id)
                REFERENCES scans(id)
                ON DELETE CASCADE,

            FOREIGN KEY (candidate_id)
                REFERENCES discovery_candidates(id)
                ON DELETE CASCADE
        )
        """)

    connection.commit()

    connection.close()


def createScan(
    query: str,
) -> int:
    """
    Create one NestScanner run and return its run ID.
    """

    currentTime = datetime.now(ZoneInfo("Asia/Singapore")).isoformat()

    connection = getConnection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO scans (
            query,
            started_at
        )
        VALUES (?, ?)
        """,
        (
            query,
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
    """
    Mark a scan as completed.
    """

    currentTime = datetime.now(ZoneInfo("Asia/Singapore")).isoformat()

    connection = getConnection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE scans
        SET completed_at = ?
        WHERE id = ?
        """,
        (
            currentTime,
            scanId,
        ),
    )

    connection.commit()

    connection.close()


def saveDiscoveryCandidate(
    scanId: int,
    discoveryCandidate: dict,
) -> int:
    """
    Save one Discovery candidate.

    Returns the database candidate ID.
    """

    candidate = discoveryCandidate["candidate"]

    discoveryEvidence = discoveryCandidate.get(
        "discoveryEvidence",
        [],
    )

    connection = getConnection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO discovery_candidates (
            run_id,
            name,
            organisation,
            source_url,
            candidate_type,
            discovery_evidence
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            scanId,
            candidate.get("name"),
            candidate.get("organisation"),
            candidate.get("sourceUrl"),
            candidate.get("candidateType"),
            json.dumps(
                discoveryEvidence,
                ensure_ascii=False,
            ),
        ),
    )

    candidateId = cursor.lastrowid

    connection.commit()

    connection.close()

    return candidateId


def saveResearchResult(
    scanId: int,
    candidateId: int,
    result: dict,
) -> int:
    """
    Save one Research result.

    Returns the database research result ID.
    """

    connection = getConnection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO research_results (
            run_id,
            candidate_id,
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
            candidateId,
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
            id,
            name,
            organisation,
            source_url,
            candidate_type,
            discovery_evidence
        FROM discovery_candidates
        WHERE run_id = ?
        ORDER BY id ASC
        """,
        (scanId,),
    )

    candidateRows = cursor.fetchall()

    connection.close()

    candidates = []

    for row in candidateRows:

        discoveryEvidence = []

        if row["discovery_evidence"]:
            try:
                discoveryEvidence = json.loads(row["discovery_evidence"])
            except json.JSONDecodeError:
                discoveryEvidence = []

        candidates.append(
            {
                "candidateId": row["id"],
                "candidate": {
                    "name": row["name"],
                    "organisation": (row["organisation"]),
                    "sourceUrl": (row["source_url"]),
                    "candidateType": (row["candidate_type"]),
                },
                "discoveryEvidence": (discoveryEvidence),
            }
        )

    return {
        "scan": dict(scanRow),
        "discovery": {
            "candidates": candidates,
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
