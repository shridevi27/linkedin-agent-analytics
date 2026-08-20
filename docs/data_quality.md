\# Data Quality Rules



\## Checks



| Check | Rule | Weight |

|---|---|---:|

| Completeness | Name and LinkedIn URL must be present | 30% |

| Uniqueness | Each lead\_key must be unique | 20% |

| Validity | SDR status must be an approved value | 20% |

| Timeliness | Each record must have an updated\_at timestamp | 15% |

| Referential integrity | Each lead must have an assigned agent | 15% |



\## Composite score



Composite DQ score = weighted average of the five checks.



\## Threshold



\- PASS: score is 95% or higher

\- FAIL: score is below 95%



\## History



Each execution appends a result to the `dq\_results` table in `analytics.sqlite3`, allowing DQ performance to be trended over time.

