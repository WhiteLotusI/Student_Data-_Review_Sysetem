# Student Data Review System

Upload a student CSV → auto-classify → validate → clean → download.

## Project Structure

```
your-repo/
├── app.py                          ← Streamlit entry point
├── requirements.txt
├── data/
│   ├── raw/                        ← auto-created at runtime
│   └── cleaned/                    ← auto-created at runtime
└── scripts/
    ├── cleaning_logic/
    │   ├── Student_attendance.py
    │   ├── Student_performance.py
    │   └── Student_profiles.py
    ├── handlers/
    │   └── error_handler.py
    ├── logs/                        ← auto-created at runtime
    └── validation/
        ├── classifier.py
        └── validator.py
```

> **Important:** `run_all.py` and `upload_logic.py` are CLI-only scripts.
> The Streamlit app replaces their functionality with a web UI — you don't
> need to deploy them.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Community Cloud

1. Push your repo to GitHub (make sure `app.py` and `requirements.txt` are
   at the **root** of the repo).

2. Go to [share.streamlit.io](https://share.streamlit.io) and click
   **New app**.

3. Select your GitHub repo, set branch to `main`, and set
   **Main file path** to `app.py`.

4. Click **Deploy** — done.

### Notes for Streamlit Cloud

- `data/raw/` and `data/cleaned/` are created automatically on first run.
  Files written there are **ephemeral** (reset on each deployment / restart).
  Use the **Download Cleaned CSV** button to save results locally.

- `scripts/logs/` validation log files are also ephemeral on the cloud.
  If you need persistent logs, consider writing them to an external store
  (S3, Google Sheets, etc.).

## Accepted CSV Formats

| Dataset | Key Columns |
|---|---|
| Student Profiles | student_id, student_name, class, gender, guardian_contact |
| Student Performance | record_id, exam_score, total_score, result, teacher_comment … |
| Attendance | attendance_id, days_present, days_absent, total_school_days … |
