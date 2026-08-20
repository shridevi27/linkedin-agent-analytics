\# Star Schema



\## Fact table



\### fact\_outreach\_event

\*\*Grain:\*\* one lead event for one agent on one date.



| Key | Meaning |

|---|---|

| outreach\_event\_key | Surrogate primary key |

| date\_key | Links to dim\_date |

| lead\_key | Links to dim\_lead |

| agent\_key | Links to dim\_agent |

| status\_key | Links to dim\_status |

| event\_type | Added, Connected, Replied, or Follow-up |

| event\_count | Always 1 |



\## Dimension tables



\### dim\_lead

One row per LinkedIn lead. Business key: LinkedIn URL.



\### dim\_agent

One row per Polluxa/LinkedIn agent.



\### dim\_status

One row per outreach status, for example Connected, Replied, Qualified, or Won.



\### dim\_date

One row per calendar date.



\## Relationships



```text

dim\_date   1 ─── \* fact\_outreach\_event

dim\_lead   1 ─── \* fact\_outreach\_event

dim\_agent  1 ─── \* fact\_outreach\_event

dim\_status 1 ─── \* fact\_outreach\_event

