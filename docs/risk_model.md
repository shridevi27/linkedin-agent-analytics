\# Risk Model



\## Method



The model uses the 95% Wilson lower confidence bound for reply rate.



\- Observed reply rate = replied leads / total leads

\- Anomaly risk score = 100 - Wilson lower confidence bound

\- Ghosting rate = leads without a reply / total leads



This method is conservative because it reduces confidence when the sample size is small.



\## Current result



\- Total leads: 4

\- Observed reply rate: 100%

\- 95% lower confidence bound: 51.01%

\- Ghosting rate: 0%

\- Anomaly risk score: 48.99%



\## Capacity recommendation



The model suggests 2 leads/day, but the configured agent safety limit is 1 lead/day. The configured safety limit takes priority.



\## Limitation



Four leads are not statistically sufficient for production decisions. These results are illustrative only.

