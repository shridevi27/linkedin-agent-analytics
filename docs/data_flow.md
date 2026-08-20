\# Data Flow



Polluxa LinkedIn Automation → CSV export → data/raw → pipeline.py → analytics.sqlite3 → Power BI dashboard



\## Incremental loading

The pipeline uses a SHA-256 file hash. When the same CSV is run again, it is skipped, so no duplicate lead is created.



\## Run metadata

Each run records start/end time, source file, rows read, rows loaded, rejected rows, status, and any error message.

