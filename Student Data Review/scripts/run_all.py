"""
Run the full Student Data Review System pipeline.

From project root:

python scripts/run_all.py
"""

from pathlib import Path

# =========================================
# IMPORT PIPELINE MODULES
# =========================================

from handlers.error_handler import (
    handle_errors,
    validate_file_type
)

from upload_logic import (
    upload_file
)

from validation.classifier import (
    classify_dataset
)

from validation.validator import (
    validate_profiles,
    validate_performance,
    validate_attendance
)

from cleaning_logic.Student_profiles import (
    clean_student_profiles
)

from cleaning_logic.Student_performance import (
    clean_student_performance
)

from cleaning_logic.Student_attendance import (
    clean_attendance_data
)


# =========================================
# PROJECT ROOT
# =========================================

ROOT = Path(__file__).resolve().parents[1]

UPLOAD_FOLDER = ROOT / "uploads"

# =========================================
# GET ALL FILES
# =========================================

uploaded_files = list(
    UPLOAD_FOLDER.glob("*.csv")
)

# =========================================
# PROCESS FILES
# =========================================

for file_path in uploaded_files:

    print("\n" + "=" * 80)
    print(f"PROCESSING: {file_path.name}")
    print("=" * 80)

    # =====================================
    # VALIDATE FILE TYPE
    # =====================================

    handle_errors(
        validate_file_type,
        file_path
    )

    # =====================================
    # SAVE FILE TO RAW FOLDER
    # =====================================

    saved_file = handle_errors(
        upload_file,
        file_path
    )

    # Skip if upload failed
    if saved_file is None:
        continue

    # =====================================
    # CLASSIFY DATASET
    # =====================================

    dataset_type = handle_errors(
        classify_dataset,
        saved_file
    )

    # Skip unknown datasets
    if dataset_type is None:

        print(
            "Dataset classification failed."
        )

        continue

    # =====================================
    # LOAD DATAFRAME
    # =====================================

    import pandas as pd

    df = pd.read_csv(saved_file)

    # =====================================
    # VALIDATE DATASET
    # =====================================

    if dataset_type == "profiles":

        handle_errors(
            validate_profiles,
            df
        )

        # =================================
        # CLEAN DATASET
        # =================================

        handle_errors(
            clean_student_profiles,
            saved_file
        )

    elif dataset_type == "performance":

        handle_errors(
            validate_performance,
            df
        )

        # =================================
        # CLEAN DATASET
        # =================================

        handle_errors(
            clean_student_performance,
            saved_file
        )

    elif dataset_type == "attendance":

        handle_errors(
            validate_attendance,
            df
        )

        # =================================
        # CLEAN DATASET
        # =================================

        handle_errors(
            clean_attendance_data,
            saved_file
        )

    else:

        print(
            f"Unknown dataset type: "
            f"{dataset_type}"
        )

print("\nPROJECT PIPELINE COMPLETE.")