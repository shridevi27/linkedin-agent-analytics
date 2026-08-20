\# LinkedIn Agent Analytics



Analytics pipeline for LinkedIn outreach data exported from Polluxa.



\## Source data

\- Lead export CSV from Polluxa

\- Raw data is stored locally in `data/raw/` and is not committed to Git.



\## Project goals

\- Load data without duplicates

\- Record every pipeline run

\- Validate data quality

\- Prepare clean data for Power BI reporting



\## Setup

1\. Create and activate the Python virtual environment.

2\. Install packages with `python -m pip install -r requirements.txt`.

3\. Run the pipeline after it is created.



\## Privacy

This project excludes raw lead data, credentials, and environment files from source control.

