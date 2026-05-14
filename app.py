"""
Student Data Review System — Streamlit App
==========================================
Upload a CSV → auto-classify → validate → clean → download results.

Run locally:
    streamlit run app.py

Project layout expected:
    app.py                          ← this file (project root)
    requirements.txt
    data/
        raw/
        cleaned/
    scripts/
        cleaning_logic/
            __init__.py
            Student_attendance.py
            Student_performance.py
            Student_profiles.py
        handlers/
            __init__.py
            error_handler.py
        logs/
        validation/
            __init__.py
            classifier.py
            validator.py
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

from cleaning_logic.Student_attendance  import clean_attendance_data
from cleaning_logic.Student_performance import clean_student_performance
from cleaning_logic.Student_profiles    import clean_student_profiles
from validation.classifier              import classify_dataset
from validation.validator               import (
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

.header-bar {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    padding: 2rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    color: white;
}
.header-bar h1 { color: white; margin: 0 0 0.25rem 0; font-size: 2rem; }
.header-bar p  { color: #a8c0cc; margin: 0; font-size: 1rem; }

.step-card {
    background: #1e2d3d;
    border: 1px solid #2c4a5e;
    border-left: 4px solid #4a9bbe;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    color: #e2e8f0;
}
.step-card b { color: #7dd3f0; }
.step-card small { color: #94a3b8; }

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

.issue-item {
    padding: 0.4rem 0.75rem;
    border-radius: 6px;
    margin: 0.25rem 0;
    font-size: 0.88rem;
}
.issue-ok   { background:#dcfce7; color:#166534; }
.issue-warn { background:#fef9c3; color:#854d0e; }

.metric-box {
    background: #1e2d3d;
    border: 1px solid #2c4a5e;
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
}
.metric-box .val { font-size: 1.8rem; font-weight: 700; color: #7dd3f0; }
.metric-box .lbl { font-size: 0.8rem; color: #94a3b8; margin-top: 0.2rem; }
</style>
""", unsafe_allow_html=True)

# ── session state init ────────────────────────────────────────────────────────
if "pipeline_result" not in st.session_state:
    st.session_state.pipeline_result = None

if "last_filename" not in st.session_state:
    st.session_state.last_filename = None

# ── helpers ──────────────────────────────────────────────────────────────────

BADGE = {
    "profiles":    '<span class="badge badge-profiles">👤 Profiles</span>',
    "performance": '<span class="badge badge-performance">📊 Performance</span>',
    "attendance":  '<span class="badge badge-attendance">📅 Attendance</span>',
}

def capture_clean(fn, path):
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


def run_pipeline(uploaded_file):
    """Run the full pipeline and return a result dict."""

    result = {
        "success":      False,
        "filename":     uploaded_file.name,
        "dataset_type": None,
        "issues":       [],
        "cleaned_df":   None,
        "raw_rows":     0,
        "logs":         "",
        "error":        None,
    }

    # read raw
    try:
        raw_df = pd.read_csv(uploaded_file)
        uploaded_file.seek(0)
    except Exception as e:
        result["error"] = f"Could not read CSV: {e}"
        return result

    result["raw_rows"] = len(raw_df)

    # normalise columns for classify + validate
    classify_df = raw_df.copy()
    classify_df.columns = (
        classify_df.columns
        .str.strip().str.lower().str.replace(" ", "_")
    )

    # classify
    try:
        dataset_type = classify_dataset(classify_df)
        result["dataset_type"] = dataset_type
    except ValueError as e:
        result["error"] = (
            f"Classification failed: {e}\n\n"
            f"Columns found: {', '.join(raw_df.columns.tolist())}"
        )
        return result

    # validate
    validate_fn = {
        "profiles":    validate_profiles,
        "performance": validate_performance,
        "attendance":  validate_attendance,
    }[dataset_type]

    try:
        result["issues"] = validate_fn(classify_df)
    except Exception as e:
        result["issues"] = [f"Validator error: {e}"]

    # save raw + clean
    try:
        raw_path = save_raw(uploaded_file)
        clean_fn = {
            "profiles":    clean_student_profiles,
            "performance": clean_student_performance,
            "attendance":  clean_attendance_data,
        }[dataset_type]
        cleaned_df, logs   = capture_clean(clean_fn, raw_path)
        result["cleaned_df"] = cleaned_df
        result["logs"]       = logs
        result["success"]    = True
    except Exception as e:
        result["error"] = f"Cleaning failed: {e}\n\n{traceback.format_exc()}"

    return result


# ── UI ───────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="header-bar">
  <h1>🎓 Student Data Review System</h1>
  <p>Upload a CSV file — the pipeline will classify, validate, and clean it automatically.</p>
</div>
""", unsafe_allow_html=True)

# ── upload ────────────────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "Drop your CSV here",
    type=["csv"],
    help="Accepted: Student Profiles · Student Performance · Attendance",
)

# clear saved results when a new file is uploaded
if uploaded and uploaded.name != st.session_state.last_filename:
    st.session_state.pipeline_result = None
    st.session_state.last_filename   = uploaded.name

if not uploaded:
    st.info("⬆️  Upload a CSV file above to get started.")

    st.markdown("#### Accepted file formats")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""<div class="step-card">
        <b>👤 Student Profiles</b><br>
        <small>student_id · student_name · class · gender · guardian_contact</small>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown("""<div class="step-card">
        <b>📊 Student Performance</b><br>
        <small>record_id · scores · results · term · subject · teacher_comment …</small>
        </div>""", unsafe_allow_html=True)

    with col3:
        st.markdown("""<div class="step-card">
        <b>📅 Attendance</b><br>
        <small>attendance_id · days_present · days_absent · total_school_days …</small>
        </div>""", unsafe_allow_html=True)

    st.stop()

# ── file info + preview ───────────────────────────────────────────────────────
st.success(f"✅ File received: **{uploaded.name}** ({uploaded.size / 1024:.1f} KB)")

try:
    preview_df = pd.read_csv(uploaded)
    uploaded.seek(0)
    with st.expander("🔍 Raw Data Preview", expanded=False):
        st.dataframe(preview_df.head(10), use_container_width=True)
        c1, c2 = st.columns(2)
        c1.markdown(f"**Rows:** {preview_df.shape[0]:,}")
        c2.markdown(f"**Columns:** {preview_df.shape[1]}")
except Exception as e:
    st.error(f"Could not preview file: {e}")
    st.stop()

st.markdown("---")

# ── run button ────────────────────────────────────────────────────────────────
if st.button("🚀 Run Pipeline", type="primary", use_container_width=True):
    with st.spinner("Running pipeline…"):
        uploaded.seek(0)
        st.session_state.pipeline_result = run_pipeline(uploaded)

# ── show results (persisted in session_state) ─────────────────────────────────
res = st.session_state.pipeline_result

if res is None:
    st.stop()

# error
if res["error"]:
    st.error("❌ Pipeline failed")
    st.code(res["error"])
    st.stop()

# ── Step 1: classification ────────────────────────────────────────────────────
badge_html = BADGE.get(
    res["dataset_type"],
    f'<span class="badge badge-unknown">{res["dataset_type"]}</span>'
)
st.markdown(f"### Step 1 — Dataset Type &nbsp;&nbsp; {badge_html}", unsafe_allow_html=True)
st.markdown(f"Detected as **{res['dataset_type']}** based on column structure.")

# ── Step 2: validation ────────────────────────────────────────────────────────
st.markdown("### Step 2 — Validation Report")
if not res["issues"]:
    st.markdown(
        '<div class="issue-item issue-ok">✅ No issues found — data looks clean!</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(f"Found **{len(res['issues'])}** issue(s):")
    for issue in res["issues"]:
        st.markdown(
            f'<div class="issue-item issue-warn">⚠️ {issue}</div>',
            unsafe_allow_html=True,
        )

# ── Step 3: cleaned results ───────────────────────────────────────────────────
st.markdown("### Step 3 — Cleaned Data")

cleaned_df   = res["cleaned_df"]
rows_before  = res["raw_rows"]
rows_after   = len(cleaned_df)
rows_removed = rows_before - rows_after

m1, m2, m3, m4 = st.columns(4)
for col_obj, val, label in [
    (m1, f"{rows_before:,}",       "Rows (original)"),
    (m2, f"{rows_after:,}",        "Rows (cleaned)"),
    (m3, f"{rows_removed:,}",      "Rows removed"),
    (m4, f"{cleaned_df.shape[1]}", "Columns"),
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
    file_name=f"{res['dataset_type']}_cleaned_{ts_label}.csv",
    mime="text/csv",
    use_container_width=True,
)

# ── logs ──────────────────────────────────────────────────────────────────────
with st.expander("📋 Pipeline Logs", expanded=False):
    st.code(
        res["logs"] if res["logs"].strip() else "No output captured.",
        language="text",
    )

st.markdown("---")
st.caption("Student Data Review System · Built with Streamlit")
