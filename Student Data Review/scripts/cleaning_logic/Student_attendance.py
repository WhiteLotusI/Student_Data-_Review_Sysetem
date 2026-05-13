from pathlib import Path
import pandas as pd
import numpy as np


# =========================
# PATH SETUP
# =========================

ROOT = Path(__file__).resolve().parents[1]

CLEAN_DIR = ROOT / "data" / "cleaned"

# Create cleaned folder if it does not exist
CLEAN_DIR.mkdir(parents=True, exist_ok=True)


def clean_attendance_data(file_path):

    # =========================
    # LOAD DATA
    # =========================

    df = pd.read_csv(file_path)

    print("\n========== ORIGINAL DATA ==========")
    print(df.head())

    # =========================
    # CLEAN COLUMN NAMES
    # =========================

    df.columns = (

        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")

    )

    # =========================
    # INSPECTION
    # =========================

    print("\n========== DATA INFO ==========")
    print(df.info())

    print("\n========== MISSING VALUES ==========")
    print(df.isnull().sum())

    print("\n========== DUPLICATES ==========")
    print(df.duplicated().sum())

    # View duplicate rows
    duplicates = df[
        df.duplicated(keep=False)
    ]

    print("\n========== DUPLICATE ROWS ==========")
    print(duplicates)

    print("\n========== COLUMN NAMES ==========")
    print(df.columns)

    print("\n========== DATA TYPES ==========")
    print(df.dtypes)

    # =========================
    # CLEAN STRING COLUMNS
    # =========================

    string_columns = [

        "attendance_id",
        "student_id",
        "student_name",
        "class",
        "term"

    ]

    for column in string_columns:

        if column in df.columns:

            df[column] = (

                df[column]
                .astype(str)
                .str.strip()

            )

    # =========================
    # FORMAT IDS
    # =========================

    if "attendance_id" in df.columns:

        df["attendance_id"] = (
            df["attendance_id"]
            .str.upper()
        )

    if "student_id" in df.columns:

        df["student_id"] = (
            df["student_id"]
            .str.upper()
        )

    # =========================
    # FORMAT NAMES
    # =========================

    if "student_name" in df.columns:

        df["student_name"] = (
            df["student_name"]
            .str.title()
        )

    # =========================
    # STANDARDIZE CLASS VALUES
    # =========================

    if "class" in df.columns:

        df["class"] = df["class"].replace({

            "jhs1": "JHS 1",
            "JHS1": "JHS 1",
            "jhs 1": "JHS 1",

            "jhs2": "JHS 2",
            "JHS2": "JHS 2",
            "jhs 2": "JHS 2",

            "jhs3": "JHS 3",
            "JHS3": "JHS 3",
            "jhs 3": "JHS 3"

        })

        df["class"] = (
            df["class"]
            .str.upper()
        )

    # =========================
    # FIX INVALID NUMERIC VALUES
    # =========================

    # Replace word values with numeric
    if "days_present" in df.columns:

        df["days_present"] = (
            df["days_present"]
            .replace("fifty", 50)
        )

    # =========================
    # CONVERT NUMERIC COLUMNS
    # =========================

    numeric_columns = [

        "days_present",
        "days_absent",
        "total_school_days",
        "attendance_percent"

    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(

                df[column],
                errors="coerce"

            )

    # =========================
    # HANDLE MISSING VALUES
    # =========================

    print("\n========== ROWS WITH MISSING VALUES ==========")

    print(
        df[df.isnull().any(axis=1)]
    )

    # Fill missing attendance percent
    required_columns = [

        "days_present",
        "total_school_days",
        "attendance_percent"

    ]

    if all(
        column in df.columns
        for column in required_columns
    ):

        df["attendance_percent"] = (

            df["attendance_percent"]

            .fillna(

                (
                    df["days_present"] /
                    df["total_school_days"]
                ) * 100

            )

        )

    # Round percentages
    if "attendance_percent" in df.columns:

        df["attendance_percent"] = (
            df["attendance_percent"]
            .round(1)
        )

    # =========================
    # REMOVE INVALID PERCENTAGES
    # =========================

    if "attendance_percent" in df.columns:

        invalid_percent = df[
            df["attendance_percent"] > 100
        ]

        print("\n========== INVALID PERCENTAGES ==========")

        print(invalid_percent)

        # Recalculate invalid percentages
        df.loc[
            df["attendance_percent"] > 100,
            "attendance_percent"
        ] = (

            (
                df["days_present"] /
                df["total_school_days"]
            ) * 100

        )

        df["attendance_percent"] = (
            df["attendance_percent"]
            .round(1)
        )

    # =========================
    # REMOVE DUPLICATES
    # =========================

    df = df.drop_duplicates()

    # Remove duplicate attendance IDs
    if "attendance_id" in df.columns:

        df = df.drop_duplicates(

            subset="attendance_id",
            keep="first"

        )

    # =========================
    # FINAL CHECKS
    # =========================

    print("\n========== CLEANED DATA INFO ==========")
    print(df.info())

    print("\n========== CLEANED MISSING VALUES ==========")
    print(df.isnull().sum())

    print("\n========== CLEANED DUPLICATES ==========")
    print(df.duplicated().sum())

    print("\n========== CLEANED DATA SAMPLE ==========")
    print(df.head())

    # =========================
    # SAVE CLEANED DATA
    # =========================

    cleaned_file = (
        CLEAN_DIR /
        "attendance_cleaned.csv"
    )

    df.to_csv(cleaned_file, index=False)

    print(
        f"\nCleaned dataset saved to:\n"
        f"{cleaned_file}"
    )

    # =========================
    # RETURN CLEANED DATAFRAME
    # =========================

    return df