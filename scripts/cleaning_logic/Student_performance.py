import pandas as pd
import numpy as np

from pathlib import Path


# =========================================
# PROJECT PATHS
# =========================================

ROOT = Path(__file__).resolve().parents[1]

CLEAN_DIR = ROOT / "data" / "cleaned"

# Create cleaned directory if it does not exist
CLEAN_DIR.mkdir(parents=True, exist_ok=True)


def clean_student_performance(file_path):

    # =========================================
    # LOAD DATASET
    # =========================================

    df = pd.read_csv(file_path)

    # =========================================
    # NORMALIZE COLUMN NAMES
    # =========================================

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # =========================================
    # INITIAL INSPECTION
    # =========================================

    print("FIRST 5 ROWS")
    print(df.head())

    print("\nDATASET SHAPE")
    print(df.shape)

    print("\nCOLUMN NAMES")
    print(df.columns)

    print("\nDATA TYPES")
    print(df.dtypes)

    print("\nDATASET INFO")
    print(df.info())

    # =========================================
    # CHECK MISSING VALUES
    # =========================================

    print("\nMISSING VALUES")
    print(df.isnull().sum())

    missing_rows = df[df.isnull().any(axis=1)]

    print("\nROWS WITH MISSING VALUES")
    print(missing_rows)

    # =========================================
    # CHECK DUPLICATES
    # =========================================

    print("\nTOTAL DUPLICATE ROWS")
    print(df.duplicated().sum())

    duplicates = df[df.duplicated(keep=False)]

    print("\nDUPLICATE ROWS")
    print(duplicates)

    if "record_id" in df.columns:

        print("\nDUPLICATE RECORD IDs")

        print(
            df["record_id"]
            .duplicated()
            .sum()
        )

        duplicate_ids = df[
            df["record_id"]
            .duplicated(keep=False)
        ]

        print("\nROWS WITH DUPLICATE RECORD IDs")

        print(duplicate_ids)

    # =========================================
    # REMOVE DUPLICATES
    # =========================================

    df = df.drop_duplicates()

    if "record_id" in df.columns:

        df = df.drop_duplicates(
            subset="record_id"
        )

    # =========================================
    # REMOVE EXTRA SPACES
    # =========================================

    text_columns = (
        df.select_dtypes(include="object")
        .columns
    )

    for column in text_columns:

        df[column] = (
            df[column]
            .astype(str)
            .str.strip()
        )

    # =========================================
    # STANDARDIZE CAPITALIZATION
    # =========================================

    # Student Names
    if "student_name" in df.columns:

        df["student_name"] = (
            df["student_name"]
            .str.title()
        )

    # Result Column
    if "result" in df.columns:

        df["result"] = df["result"].replace({

            "PASS": "Pass",
            "pass": "Pass",
            "passed": "Pass",
            "P": "Pass",

            "Fail ": "Fail",
            "failed": "Fail",
            "F": "Fail"

        })

    # Class Column
    if "class" in df.columns:

        df["class"] = df["class"].replace({

            "jhs 1": "JHS 1",
            "jhs1": "JHS 1",
            "Js 1": "JHS 1",
            "Form 1": "JHS 1",
            "JHS1": "JHS 1",

            "jhs 2": "JHS 2",
            "jhs2": "JHS 2",
            "js 2": "JHS 2",
            "Form 2": "JHS 2",
            "JHS2": "JHS 2",

            "jhs 3": "JHS 3",
            "jhs3": "JHS 3",
            "js 3": "JHS 3",
            "Form 3": "JHS 3",
            "JHS3": "JHS 3"
        })

    # Teacher Comments
    if "teacher_comment" in df.columns:

        df["teacher_comment"] = (
            df["teacher_comment"]
            .str.title()
        )

    # =========================================
    # CHECK UNIQUE VALUES
    # =========================================

    if "result" in df.columns:

        print("\nUNIQUE VALUES - RESULTS")
        print(df["result"].unique())

    if "class" in df.columns:

        print("\nUNIQUE VALUES - CLASS")
        print(df["class"].unique())

    if "gender" in df.columns:

        print("\nUNIQUE VALUES - GENDER")
        print(df["gender"].unique())

    if "term" in df.columns:

        print("\nUNIQUE VALUES - TERM")
        print(df["term"].unique())

    # =========================================
    # CONVERT NUMERIC COLUMNS
    # =========================================

    numeric_columns = [

        "attendance_percent",
        "assignment_score",
        "quiz_score",
        "exam_score",
        "total_score",
        "study_hours"

    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # =========================================
    # CHECK INVALID NUMERIC VALUES
    # =========================================

    # Attendance percent: 0-100
    if "attendance_percent" in df.columns:

        invalid_attendance = df[

            (df["attendance_percent"] < 0) |
            (df["attendance_percent"] > 100)

        ]

        print("\nINVALID ATTENDANCE VALUES")
        print(invalid_attendance)

        df.loc[
            (df["attendance_percent"] < 0) |
            (df["attendance_percent"] > 100),
            "attendance_percent"
        ] = np.nan

    # Assignment score: 0-20
    if "assignment_score" in df.columns:

        invalid_assignment = df[

            (df["assignment_score"] < 0) |
            (df["assignment_score"] > 20)

        ]

        print("\nINVALID ASSIGNMENT SCORES")
        print(invalid_assignment)

    # Quiz score: 0-20
    if "quiz_score" in df.columns:

        invalid_quiz = df[

            (df["quiz_score"] < 0) |
            (df["quiz_score"] > 20)

        ]

        print("\nINVALID QUIZ SCORES")
        print(invalid_quiz)

    # Exam score: 0-60
    if "exam_score" in df.columns:

        invalid_exam = df[

            (df["exam_score"] < 0) |
            (df["exam_score"] > 60)

        ]

        print("\nINVALID EXAM SCORES")
        print(invalid_exam)

    # Total score: 0-100
    if "total_score" in df.columns:

        invalid_total = df[

            (df["total_score"] < 0) |
            (df["total_score"] > 100)

        ]

        print("\nINVALID TOTAL SCORES")
        print(invalid_total)

    # =========================================
    # HANDLE MISSING VALUES
    # =========================================

    print("\nMISSING VALUES BEFORE CLEANING")
    print(df.isnull().sum())

    # Fill numeric missing values using median
    for column in numeric_columns:

        if column in df.columns:

            df[column] = (
                df[column]
                .fillna(df[column].median())
            )

    # Fill missing student names
    if (
        "student_name" in df.columns and
        "student_id" in df.columns
    ):

        df["student_name"] = (

            df.groupby("student_id")[
                "student_name"
            ]

            .transform(

                lambda values:

                values.fillna(

                    values.mode()[0]

                    if not values.mode().empty
                    else "Unknown"

                )

            )

        )

    # =========================================
    # RECALCULATE TOTAL SCORE
    # =========================================

    required_score_columns = [

        "assignment_score",
        "quiz_score",
        "exam_score"

    ]

    if all(
        column in df.columns
        for column in required_score_columns
    ):

        df["total_score"] = (

            df["assignment_score"] +
            df["quiz_score"] +
            df["exam_score"]

        )

    # =========================================
    # RECALCULATE RESULTS
    # =========================================

    if "total_score" in df.columns:

        df["result"] = np.where(

            df["total_score"] >= 50,
            "Pass",
            "Fail"

        )

    # =========================================
    # FINAL VALIDATION
    # =========================================

    print("\nFINAL MISSING VALUES")
    print(df.isnull().sum())

    print("\nFINAL DATA TYPES")
    print(df.dtypes)

    if "result" in df.columns:

        print("\nFINAL UNIQUE RESULTS")
        print(df["result"].unique())

    if "class" in df.columns:

        print("\nFINAL UNIQUE CLASSES")
        print(df["class"].unique())

    print("\nFINAL DATASET SHAPE")
    print(df.shape)

    # =========================================
    # SAVE CLEANED DATASET
    # =========================================

    cleaned_file = (
        CLEAN_DIR /
        "cleaned_student_performance_data.csv"
    )

    df.to_csv(cleaned_file, index=False)

    print("\nDATA CLEANING COMPLETE")

    print(
        f"Cleaned dataset saved to:\n"
        f"{cleaned_file}"
    )

    # =========================================
    # RETURN CLEANED DATAFRAME
    # =========================================

    return df