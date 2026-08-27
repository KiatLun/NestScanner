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
    # SCAN RUNS
    # =================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_runs (
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
                REFERENCES scan_runs(id)
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

            profile TEXT,
            research_evidence TEXT,

            FOREIGN KEY (run_id)
                REFERENCES scan_runs(id)
                ON DELETE CASCADE,

            FOREIGN KEY (candidate_id)
                REFERENCES discovery_candidates(id)
                ON DELETE CASCADE
        )
        """)

    connection.commit()

    connection.close()


def createScanRun(
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
        INSERT INTO scan_runs (
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

    runId = cursor.lastrowid

    connection.commit()

    connection.close()

    return runId


def completeScanRun(
    runId: int,
):
    """
    Mark a scan run as completed.
    """

    currentTime = datetime.now(ZoneInfo("Asia/Singapore")).isoformat()

    connection = getConnection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE scan_runs
        SET completed_at = ?
        WHERE id = ?
        """,
        (
            currentTime,
            runId,
        ),
    )

    connection.commit()

    connection.close()


def saveDiscoveryCandidate(
    runId: int,
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
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            runId,
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
    runId: int,
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
            profile,
            research_evidence
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            runId,
            candidateId,
            result.get("releaseDate"),
            result.get("isRecent"),
            result.get("isLocallyDeployable"),
            json.dumps(
                result.get("profile"),
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
