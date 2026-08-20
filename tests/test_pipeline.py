import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = ROOT / "data" / "processed" / "analytics.sqlite3"


def test_one_lead_was_loaded():
    with sqlite3.connect(DATABASE_PATH) as connection:
        count = connection.execute("SELECT COUNT(*) FROM leads").fetchone()[0]

    assert count == 1


def test_pipeline_run_was_recorded():
    with sqlite3.connect(DATABASE_PATH) as connection:
        count = connection.execute(
            "SELECT COUNT(*) FROM pipeline_runs WHERE status IN ('success', 'skipped')"
        ).fetchone()[0]

    assert count >= 2