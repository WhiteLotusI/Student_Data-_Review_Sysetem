"""
Student Data Review System — Streamlit App
==========================================
Upload a CSV → auto-classify → validate → clean → download results.

Run locally:
    streamlit run app.py

Project layout expected:
    app.py                          ← this file (project root)
    scripts/
        cleaning_logic/
            Student_attendance.py
            Student_performance.py
            Student_profiles.py
        handlers/
            error_handler.py
        validation/
            classifier.py
            validator.py
    data/
        raw/
        cleaned/
    scripts/logs/
"""

import sys
import io
import traceback
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st

# ── make sure `scripts/` is importable ──────────────────────────────────────
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))

from scripts.cleaning_logic.Student_attendance  import clean_attendance_data
from scripts.cleaning_logic.Student_performance import clean_student_performance
from scripts.cleaning_logic.Student_profiles    import clean_student_profiles
from scripts.validation.classifier              import classify_dataset
from scripts.validation.validator               import (
    validate_profiles,
    validate_performance,
    validate_attendance,
)

# ── directory setup ──────────────────────────────────────────────────────────
RAW_DIR   = ROOT / "data" / "raw"
CLEAN_DIR = ROOT / "data" / "cleaned"
LOG_DIR   = ROOT / "scripts" / "logs"

for d in (RAW_DIR, CLEAN_DIR, LOG_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ── page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Student Data Review",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
h1, h2, h3 {
    font-family: 'DM Serif Display', serif;
}

/* gradient header bar */
.header-bar {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    padding: 2rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    color: white;
}
.header-bar h1 { color: white; margin: 0 0 0.25rem 0; font-size: 2rem; }
.header-bar p  { color: #a8c0cc; margin: 0; font-size: 1rem; }

/* step cards */
.step-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #2c5364;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
}

/* badge */
.badge {
    display: inline-block;
    padding: 0.2rem 0.75rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.04em;
}
.badge-profiles    { background:#dbeafe; color:#1e40af; }
.badge-performance { background:#dcfce7; color:#166534; }
.badge-attendance  { background:#fef9c3; color:#854d0e; }
.badge-unknown     { background:#fee2e2; color:#991b1b; }

/* issue list */
.issue-item {
    padding: 0.4rem 0.75rem;
    border-radius: 6px;
    margin: 0.25rem 0;
    font-size: 0.88rem;
}
.issue-ok   { background:#dcfce7; color:#166534; }
.issue-warn { background:#fef9c3; color:#854d0e; }

/* metric box */
.metric-box {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
}
.metric-box .val { font-size: 1.8rem; font-weight: 700; color: #2c5364; }
.metric-box .lbl { font-size: 0.8rem; color: #64748b; margin-top: 0.2rem; }
</style>
""", unsafe_allow_html=True)

# ── helpers ──────────────────────────────────────────────────────────────────

BADGE = {
    "profiles":    '<span class="badge badge-profiles">👤 Profiles</span>',
    "performance": '<span class="badge badge-performance">📊 Performance</span>',
    "attendance":  '<span class="badge badge-attendance">📅 Attendance</span>',
}

def capture_clean(fn, path):
    """Run a cleaning function and capture its stdout logs."""
    buf = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = buf
    try:
        result = fn(path)
    except Exception:
        sys.stdout = old_stdout
        raise
    finally:
        sys.stdout = old_stdout
    return result, buf.getvalue()


def save_raw(uploaded_file) -> Path:
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = Path(uploaded_file.name).stem
    dest = RAW_DIR / f"{name}_{ts}.csv"
    dest.write_bytes(uploaded_file.getbuffer())
    return dest


# ── UI ───────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="header-bar">
  <h1>🎓 Student Data Review System</h1>
  <p>Upload a CSV file — the pipeline will classify, validate, and clean it automatically.</p>
</div>
""", unsafe_allow_html=True)

# ── upload zone ──────────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "Drop your CSV here",
    type=["csv"],
    help="Accepted formats: Student Profiles · Student Performance · Attendance",
)

if not uploaded:
    st.info("⬆️  Upload a CSV file above to get started.")

    st.markdown("#### Accepted file formats")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="step-card">
        <b>👤 Student Profiles</b><br>
        <small>student_id · student_name · class · gender · guardian_contact</small>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="step-card">
        <b>📊 Student Performance</b><br>
        <small>record_id · scores · results · term · subject · teacher_comment …</small>
        </div>""", unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="step-card">
        <b>📅 Attendance</b><br>
        <small>attendance_id · days_present · days_absent · total_school_days …</small>
        </div>""", unsafe_allow_html=True)

    st.stop()

# ── file received ─────────────────────────────────────────────────────────────
st.success(f"✅ File received: **{uploaded.name}** ({uploaded.size / 1024:.1f} KB)")

# read for preview + classify
try:
    raw_df = pd.read_csv(uploaded)
    uploaded.seek(0)           # reset for later saving
except Exception as e:
    st.error(f"Could not read CSV: {e}")
    st.stop()

# ── raw preview ──────────────────────────────────────────────────────────────
with st.expander("🔍 Raw Data Preview", expanded=False):
    st.dataframe(raw_df.head(10), use_container_width=True)
    c1, c2 = st.columns(2)
    c1.markdown(f"**Rows:** {raw_df.shape[0]:,}")
    c2.markdown(f"**Columns:** {raw_df.shape[1]}")

# ── run pipeline button ───────────────────────────────────────────────────────
st.markdown("---")
run = st.button("🚀 Run Pipeline", type="primary", use_container_width=True)

if not run:
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# PIPELINE
# ─────────────────────────────────────────────────────────────────────────────

progress = st.progress(0, text="Starting pipeline…")

# ── STEP 1 · classify ─────────────────────────────────────────────────────────
progress.progress(15, text="Step 1 / 3 — Classifying dataset…")

# normalise columns the same way cleaning scripts do (lowercase + underscore)
classify_df = raw_df.copy()
classify_df.columns = (
    classify_df.columns
    .str.strip().str.lower().str.replace(" ", "_")
)

try:
    dataset_type = classify_dataset(classify_df)
except ValueError as e:
    progress.empty()
    st.error(f"❌ Classification failed: {e}")
    st.markdown("**Columns found in your file:**")
    st.code(", ".join(raw_df.columns.tolist()))
    st.stop()

badge_html = BADGE.get(dataset_type, f'<span class="badge badge-unknown">{dataset_type}</span>')
st.markdown(f"### Step 1 — Dataset Type &nbsp;&nbsp; {badge_html}", unsafe_allow_html=True)
st.markdown(f"Detected as **{dataset_type}** based on column structure.")

# ── STEP 2 · validate ─────────────────────────────────────────────────────────
progress.progress(40, text="Step 2 / 3 — Validating data…")

validate_fn = {
    "profiles":    validate_profiles,
    "performance": validate_performance,
    "attendance":  validate_attendance,
}[dataset_type]

try:
    issues = validate_fn(classify_df)
except Exception as e:
    issues = [f"Validator crashed: {e}"]

st.markdown("### Step 2 — Validation Report")

if not issues:
    st.markdown('<div class="issue-item issue-ok">✅ No issues found — data looks clean!</div>',
                unsafe_allow_html=True)
else:
    st.markdown(f"Found **{len(issues)}** issue(s):")
    for issue in issues:
        st.markdown(f'<div class="issue-item issue-warn">⚠️ {issue}</div>',
                    unsafe_allow_html=True)

# ── STEP 3 · clean ────────────────────────────────────────────────────────────
progress.progress(65, text="Step 3 / 3 — Running cleaning pipeline…")

# save raw file to disk so cleaning scripts can read it via path
raw_path = save_raw(uploaded)

clean_fn = {
    "profiles":    clean_student_profiles,
    "performance": clean_student_performance,
    "attendance":  clean_attendance_data,
}[dataset_type]

try:
    cleaned_df, logs = capture_clean(clean_fn, raw_path)
except Exception as e:
    progress.empty()
    st.error(f"❌ Cleaning failed: {e}")
    with st.expander("Traceback"):
        st.code(traceback.format_exc())
    st.stop()

progress.progress(100, text="Pipeline complete ✅")

# ── results ───────────────────────────────────────────────────────────────────
st.markdown("### Step 3 — Cleaned Data")

rows_before = raw_df.shape[0]
rows_after  = cleaned_df.shape[0]
rows_removed = rows_before - rows_after
cols = cleaned_df.shape[1]

m1, m2, m3, m4 = st.columns(4)
for col_obj, val, label in [
    (m1, f"{rows_before:,}",  "Rows (original)"),
    (m2, f"{rows_after:,}",   "Rows (cleaned)"),
    (m3, f"{rows_removed:,}", "Rows removed"),
    (m4, f"{cols}",           "Columns"),
]:
    col_obj.markdown(
        f'<div class="metric-box"><div class="val">{val}</div>'
        f'<div class="lbl">{label}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("")
st.dataframe(cleaned_df.head(20), use_container_width=True)

# ── download ──────────────────────────────────────────────────────────────────
st.markdown("#### ⬇️  Download")

csv_bytes = cleaned_df.to_csv(index=False).encode("utf-8")
ts_label  = datetime.now().strftime("%Y%m%d_%H%M%S")

st.download_button(
    label="Download Cleaned CSV",
    data=csv_bytes,
    file_name=f"{dataset_type}_cleaned_{ts_label}.csv",
    mime="text/csv",
    use_container_width=True,
)

# ── pipeline logs ──────────────────────────────────────────────────────────────
with st.expander("📋 Pipeline Logs (cleaning script output)", expanded=False):
    st.code(logs if logs.strip() else "No console output captured.", language="text")

st.markdown("---")
st.caption("Student Data Review System · Built with Streamlit")
