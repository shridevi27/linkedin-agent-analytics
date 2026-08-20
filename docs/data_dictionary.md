\# Data Dictionary



| Column | Type | Business definition |

|---|---|---|

| lead\_key | Text | Unique business key: LinkedIn URL, or a generated fallback key |

| name | Text | Lead’s displayed name |

| job\_title | Text | Lead’s job title/headline |

| company | Text | Lead’s company name |

| industry | Text | Lead’s industry |

| location | Text | Lead’s location |

| agent | Text | Polluxa LinkedIn agent that handled the lead |

| sdr\_status | Text | Current outreach status, such as connected or replied |

| source | Text | Source from which the lead entered Polluxa |

| linkedin\_url | Text | LinkedIn profile URL; treated as personal data |

| added\_on | Date | Date the lead was added to the agent pipeline |

| last\_contacted | DateTime | Most recent outreach date/time |

| connected\_at | DateTime | Date/time the LinkedIn connection was accepted |

| source\_hash | Text | SHA-256 hash of the source CSV file |

| updated\_at | DateTime | UTC timestamp of the pipeline load/update |



\## Pipeline run fields



| Column | Type | Business definition |

|---|---|---|

| run\_id | Text | Unique identifier for one pipeline execution |

| started\_at | DateTime | UTC start time |

| ended\_at | DateTime | UTC end time |

| rows\_read | Integer | Rows read from the CSV |

| rows\_loaded | Integer | Valid rows inserted or updated |

| rows\_rejected | Integer | Rows rejected by validation |

| status | Text | running, success, failed, or skipped |

| error\_message | Text | Failure details, when applicable |

