import math
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = ROOT / "data" / "processed" / "analytics.sqlite3"


def wilson_lower_bound(successes, total, z=1.96):
    """Conservative lower confidence bound for a response rate."""
    if total == 0:
        return 0.0

    proportion = successes / total
    denominator = 1 + (z * z / total)
    centre = proportion + (z * z / (2 * total))
    margin = z * math.sqrt(
        (proportion * (1 - proportion) / total) + (z * z / (4 * total * total))
    )
    return max(0.0, (centre - margin) / denominator)


with sqlite3.connect(DATABASE_PATH) as connection:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS risk_results (
            calculated_at TEXT NOT NULL,
            total_leads INTEGER NOT NULL,
            replied_leads INTEGER NOT NULL,
            reply_rate REAL NOT NULL,
            wilson_lower_bound REAL NOT NULL,
            ghosting_rate REAL NOT NULL,
            anomaly_risk_score REAL NOT NULL,
            recommended_daily_capacity INTEGER NOT NULL,
            notes TEXT NOT NULL
        )
        """
    )

    statuses = [
        row[0].strip().lower()
        for row in connection.execute("SELECT sdr_status FROM leads").fetchall()
    ]

    total = len(statuses)
    replied = sum(status == "replied" for status in statuses)
    reply_rate = round((replied / total) * 100, 2) if total else 0.0
    lower_bound = round(wilson_lower_bound(replied, total) * 100, 2)
    ghosting_rate = round(((total - replied) / total) * 100, 2) if total else 0.0

    # Higher risk means lower confidence in outreach performance.
    anomaly_risk_score = round(100 - lower_bound, 2)

    if anomaly_risk_score >= 70:
        recommended_capacity = 1
    elif anomaly_risk_score >= 40:
        recommended_capacity = 2
    else:
        recommended_capacity = 3

    notes = (
        "Illustrative result only: dataset is small. "
        "Use the agent's configured safety limit if it is lower."
    )

    connection.execute(
        "INSERT INTO risk_results VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            datetime.now(timezone.utc).isoformat(),
            total,
            replied,
            reply_rate,
            lower_bound,
            ghosting_rate,
            anomaly_risk_score,
            recommended_capacity,
            notes,
        ),
    )
    connection.commit()

print(f"Total leads: {total}")
print(f"Replied leads: {replied}")
print(f"Reply rate: {reply_rate}%")
print(f"Wilson lower confidence bound: {lower_bound}%")
print(f"Ghosting/no-reply rate: {ghosting_rate}%")
print(f"Anomaly risk score: {anomaly_risk_score}%")
print(f"Recommended daily capacity: {recommended_capacity}")
print("Note: This is illustrative because the sample size is small.")