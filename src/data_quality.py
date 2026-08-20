import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = ROOT / "data" / "processed" / "analytics.sqlite3"
VALID_STATUSES = {"new", "contacted", "connected", "replied", "qualified", "won"}
PASS_THRESHOLD = 95.0


def percentage(numerator, denominator):
    return round((numerator / denominator) * 100, 2) if denominator else 0.0


with sqlite3.connect(DATABASE_PATH) as connection:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS dq_results (
            checked_at TEXT NOT NULL,
            total_rows INTEGER NOT NULL,
            completeness_score REAL NOT NULL,
            uniqueness_score REAL NOT NULL,
            validity_score REAL NOT NULL,
            timeliness_score REAL NOT NULL,
            referential_integrity_score REAL NOT NULL,
            composite_score REAL NOT NULL,
            passed INTEGER NOT NULL
        )
        """
    )

    rows = connection.execute(
        "SELECT lead_key, name, agent, sdr_status, linkedin_url, updated_at FROM leads"
    ).fetchall()

    total = len(rows)

    complete = sum(bool(name and linkedin_url) for _, name, _, _, linkedin_url, _ in rows)
    unique = len({lead_key for lead_key, *_ in rows})
    valid = sum(status in VALID_STATUSES for _, _, _, status, _, _ in rows)
    timely = sum(bool(updated_at) for *_, updated_at in rows)
    agent_present = sum(bool(agent) for _, _, agent, _, _, _ in rows)

    completeness = percentage(complete, total)
    uniqueness = percentage(unique, total)
    validity = percentage(valid, total)
    timeliness = percentage(timely, total)
    referential_integrity = percentage(agent_present, total)

    composite = round(
        completeness * 0.30
        + uniqueness * 0.20
        + validity * 0.20
        + timeliness * 0.15
        + referential_integrity * 0.15,
        2,
    )
    passed = int(composite >= PASS_THRESHOLD)

    connection.execute(
        """
        INSERT INTO dq_results VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now(timezone.utc).isoformat(),
            total,
            completeness,
            uniqueness,
            validity,
            timeliness,
            referential_integrity,
            composite,
            passed,
        ),
    )
    connection.commit()

print(f"Completeness: {completeness}%")
print(f"Uniqueness: {uniqueness}%")
print(f"Validity: {validity}%")
print(f"Timeliness: {timeliness}%")
print(f"Referential integrity: {referential_integrity}%")
print(f"Composite DQ score: {composite}%")
print("DQ result:", "PASS" if passed else "FAIL")