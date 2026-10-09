
import json
import sqlite3
from datetime import datetime

import app.storage.incident_store as store
from app.core.models import Incident, ProcessEvidence


def test_save_incident_persists_structured_evidence(tmp_path, monkeypatch):
    database_path = tmp_path / "aegis_test.db"
    monkeypatch.setattr(store, "DATABASE_PATH", database_path)

    store.initialize_database()

    timestamp = datetime(2026, 10, 8, 12, 0, 0)

    incident = Incident(
        timestamp=timestamp,
        type="HIGH_CPU",
        message="System CPU usage is elevated",
        evidence=[
            ProcessEvidence(
                pid=1234,
                name="python.exe",
                cpu_percent=85.0,
                memory_percent=2.5,
            )
        ],
    )

    incident_id = store.save_incident(incident)

    assert incident_id == 1

    with sqlite3.connect(database_path) as connection:
        row = connection.execute(
            """
            SELECT timestamp, incident_type, message, evidence_json
            FROM incidents
            WHERE id = ?
            """,
            (incident_id,),
        ).fetchone()

    assert row is not None
    assert row[0] == timestamp.isoformat()
    assert row[1] == "HIGH_CPU"
    assert row[2] == "System CPU usage is elevated"

    evidence = json.loads(row[3])
    assert evidence[0]["pid"] == 1234
    assert evidence[0]["name"] == "python.exe"
    assert evidence[0]["cpu_percent"] == 85.0