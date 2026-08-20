import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = ROOT / "data" / "processed" / "analytics.sqlite3"
OUTPUT_DIR = ROOT / "data" / "processed"


def export_table(connection, table_name):
    output_file = OUTPUT_DIR / f"{table_name}.csv"

    columns = [
        row[1]
        for row in connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    ]
    rows = connection.execute(f"SELECT * FROM {table_name}").fetchall()

    with output_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(columns)
        writer.writerows(rows)

    print(f"Created: {output_file.name} ({len(rows)} rows)")


with sqlite3.connect(DATABASE_PATH) as connection:
    export_table(connection, "leads")
    export_table(connection, "dq_results")
    export_table(connection, "risk_results")