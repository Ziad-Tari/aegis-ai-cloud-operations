
import json
import sqlite3
from dataclasses import asdict
from pathlib import Path

from app.core.models import Incident, Investigation


DATABASE_PATH = Path(__file__).resolve().parents[2] / "data" / "aegis.db"


def initialize_database() -> None:
    """Create the database and migrate older incident tables."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                incident_type TEXT NOT NULL,
                message TEXT NOT NULL,
                evidence_json TEXT NOT NULL,
                investigation_json TEXT
            )
            """
        )

        columns = {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(incidents)"
            ).fetchall()
        }

        if "investigation_json" not in columns:
            connection.execute(
                "ALTER TABLE incidents ADD COLUMN investigation_json TEXT"
            )


def save_incident(
    incident: Incident,
    investigation: Investigation | None = None,
) -> int:
    """Persist an incident and optional investigation; return its ID."""
    initialize_database()

    evidence_json = json.dumps(
        [asdict(item) for item in incident.evidence]
    )
    investigation_json = (
        json.dumps(asdict(investigation))
        if investigation is not None
        else None
    )

    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.execute(
            """
            INSERT INTO incidents (
                timestamp,
                incident_type,
                message,
                evidence_json,
                investigation_json
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                incident.timestamp.isoformat(),
                incident.type,
                incident.message,
                evidence_json,
                investigation_json,
            ),
        )
        return int(cursor.lastrowid)


def _row_to_dict(row: tuple) -> dict:
    return {
        "id": row[0],
        "timestamp": row[1],
        "incident_type": row[2],
        "message": row[3],
        "evidence": json.loads(row[4]),
        "investigation": (
            json.loads(row[5]) if row[5] is not None else None
        ),
    }


def list_incidents(limit: int = 50, offset: int = 0) -> list[dict]:
    """Return newest incidents first, with pagination."""
    if not 1 <= limit <= 200:
        raise ValueError("limit must be between 1 and 200")
    if offset < 0:
        raise ValueError("offset cannot be negative")

    initialize_database()

    with sqlite3.connect(DATABASE_PATH) as connection:
        rows = connection.execute(
            """
            SELECT id, timestamp, incident_type, message,
                   evidence_json, investigation_json
            FROM incidents
            ORDER BY id DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()

    return [_row_to_dict(row) for row in rows]


def get_incident(incident_id: int) -> dict | None:
    """Return one incident by ID, or None if it does not exist."""
    initialize_database()

    with sqlite3.connect(DATABASE_PATH) as connection:
        row = connection.execute(
            """
            SELECT id, timestamp, incident_type, message,
                   evidence_json, investigation_json
            FROM incidents
            WHERE id = ?
            """,
            (incident_id,),
        ).fetchone()

    return _row_to_dict(row) if row else None