from __future__ import annotations

import csv
import hashlib
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
STAGING_DIR = ROOT / "data" / "staging"
DATABASE_PATH = ROOT / "data" / "processed" / "analytics.sqlite3"

VALID_STATUSES = {"new", "contacted", "connected", "replied", "qualified", "won"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lead_key(row: dict[str, str]) -> str:
    linkedin_url = row.get("LinkedIn URL", "").strip().lower()
    if linkedin_url:
        return linkedin_url

    fallback = "|".join(
        [
            row.get("Name", "").strip().lower(),
            row.get("Added On", "").strip(),
            row.get("Company", "").strip().lower(),
        ]
    )
    return hashlib.sha256(fallback.encode("utf-8")).hexdigest()


def create_tables(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS pipeline_runs (
            run_id TEXT PRIMARY KEY,
            started_at TEXT NOT NULL,
            ended_at TEXT,
            source_file TEXT NOT NULL,
            source_hash TEXT NOT NULL,
            rows_read INTEGER NOT NULL DEFAULT 0,
            rows_loaded INTEGER NOT NULL DEFAULT 0,
            rows_rejected INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL,
            error_message TEXT
        );

        CREATE TABLE IF NOT EXISTS ingested_files (
            source_hash TEXT PRIMARY KEY,
            source_file TEXT NOT NULL,
            ingested_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS leads (
            lead_key TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            job_title TEXT,
            company TEXT,
            industry TEXT,
            location TEXT,
            agent TEXT,
            sdr_status TEXT,
            source TEXT,
            linkedin_url TEXT,
            added_on TEXT,
            last_contacted TEXT,
            connected_at TEXT,
            source_hash TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
    )


def validate_row(row: dict[str, str]) -> str | None:
    if not row.get("Name", "").strip():
        return "Name is required"

    status = row.get("SDR Status", "").strip().lower()
    if status and status not in VALID_STATUSES:
        return f"Unknown SDR Status: {status}"

    return None


def latest_csv() -> Path:
    files = sorted(RAW_DIR.glob("*.csv"), key=lambda item: item.stat().st_mtime)
    if not files:
        raise FileNotFoundError(f"No CSV files found in {RAW_DIR}")
    return files[-1]


def run_pipeline() -> None:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    source_file = latest_csv()
    source_hash = file_hash(source_file)
    run_id = str(uuid.uuid4())
    started_at = utc_now()

    with sqlite3.connect(DATABASE_PATH) as connection:
        create_tables(connection)

        already_loaded = connection.execute(
            "SELECT 1 FROM ingested_files WHERE source_hash = ?",
            (source_hash,),
        ).fetchone()

        if already_loaded:
            connection.execute(
                """
                INSERT INTO pipeline_runs
                (run_id, started_at, ended_at, source_file, source_hash, status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (run_id, started_at, utc_now(), source_file.name, source_hash, "skipped"),
            )
            print("No changes found. File was already loaded; no duplicates created.")
            return

        connection.execute(
            """
            INSERT INTO pipeline_runs
            (run_id, started_at, source_file, source_hash, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (run_id, started_at, source_file.name, source_hash, "running"),
        )

        rows_read = 0
        rows_loaded = 0
        rows_rejected = 0

        try:
            with source_file.open("r", encoding="utf-8-sig", newline="") as csv_file:
                reader = csv.DictReader(csv_file)

                for row in reader:
                    rows_read += 1
                    error = validate_row(row)

                    if error:
                        rows_rejected += 1
                        print(f"Rejected row {rows_read}: {error}")
                        continue

                    connection.execute(
                        """
                        INSERT INTO leads (
                            lead_key, name, job_title, company, industry, location,
                            agent, sdr_status, source, linkedin_url, added_on,
                            last_contacted, connected_at, source_hash, updated_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(lead_key) DO UPDATE SET
                            name = excluded.name,
                            job_title = excluded.job_title,
                            company = excluded.company,
                            industry = excluded.industry,
                            location = excluded.location,
                            agent = excluded.agent,
                            sdr_status = excluded.sdr_status,
                            source = excluded.source,
                            linkedin_url = excluded.linkedin_url,
                            added_on = excluded.added_on,
                            last_contacted = excluded.last_contacted,
                            connected_at = excluded.connected_at,
                            source_hash = excluded.source_hash,
                            updated_at = excluded.updated_at
                        """,
                        (
                            lead_key(row),
                            row.get("Name", "").strip(),
                            row.get("Job Title", "").strip(),
                            row.get("Company", "").strip(),
                            row.get("Industry", "").strip(),
                            row.get("Location", "").strip(),
                            row.get("Agent", "").strip(),
                            row.get("SDR Status", "").strip().lower(),
                            row.get("Source", "").strip(),
                            row.get("LinkedIn URL", "").strip(),
                            row.get("Added On", "").strip(),
                            row.get("Last Contacted", "").strip(),
                            row.get("Connected At", "").strip(),
                            source_hash,
                            utc_now(),
                        ),
                    )
                    rows_loaded += 1

            connection.execute(
                "INSERT INTO ingested_files (source_hash, source_file, ingested_at) VALUES (?, ?, ?)",
                (source_hash, source_file.name, utc_now()),
            )

            connection.execute(
                """
                UPDATE pipeline_runs
                SET ended_at = ?, rows_read = ?, rows_loaded = ?, rows_rejected = ?, status = ?
                WHERE run_id = ?
                """,
                (utc_now(), rows_read, rows_loaded, rows_rejected, "success", run_id),
            )
            connection.commit()
            print(f"Success: read={rows_read}, loaded={rows_loaded}, rejected={rows_rejected}")

        except Exception as error:
            connection.execute(
                """
                UPDATE pipeline_runs
                SET ended_at = ?, rows_read = ?, rows_loaded = ?, rows_rejected = ?,
                    status = ?, error_message = ?
                WHERE run_id = ?
                """,
                (utc_now(), rows_read, rows_loaded, rows_rejected, "failed", str(error), run_id),
            )
            connection.commit()
            raise


if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception as exc:
        print(f"Pipeline failed: {exc}", file=sys.stderr)
        sys.exit(1)