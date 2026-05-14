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


def clean_student_profiles(file_path):

    # =========================
    # LOAD DATA
    # =========================
    df = pd.read_csv(file_path)

    print("\n========== ORIGINAL DATA ==========")
    print(df.head())

    # =========================
    # COLUMN NORMALIZATION
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

    # =========================
    # CLEAN STRING COLUMNS
    # =========================
    string_columns = [
        "student_id",
        "student_name",
        "class",
        "gender",
        "guardian_contact"
    ]

    for column in string_columns:

        if column in df.columns:

            df[column] = (
                df[column]
                .astype(str)
                .str.strip()
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
    # FORMAT IDS
    # =========================
    if "student_id" in df.columns:

        df["student_id"] = (
            df["student_id"]
            .str.upper()
        )

    # =========================
    # FIX GENDER VALUES
    # =========================
    if "gender" in df.columns:

        df["gender"] = df["gender"].replace({

            "M": "Male",
            "m": "Male",
            "MALE": "Male",
            "male": "Male",
            "Mal": "Male",
            "Mle": "Male",
            "Man": "Male",
            "boy": "Male",
            "B": "Male",

            "F": "Female",
            "f": "Female",
            "FEMALE": "Female",
            "female": "Female",
            "Femal": "Female",
            "Fmeale": "Female",
            "Woman": "Female",
            "girl": "Female",
            "G": "Female"

        })

        df["gender"] = (
            df["gender"]
            .str.title()
        )

    # =========================
    # FIX CLASS VALUES
    # =========================
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

        df["class"] = (
            df["class"]
            .str.upper()
        )

    # =========================
    # HANDLE MISSING VALUES
    # =========================

    # Replace empty strings with NaN
    df.replace("", np.nan, inplace=True)

    # Remove rows with missing student_id
    if "student_id" in df.columns:

        df = df.dropna(
            subset=["student_id"]
        )

    # Fill missing guardian contacts
    if "guardian_contact" in df.columns:

        df["guardian_contact"] = (
            df["guardian_contact"]
            .fillna("Not Provided")
        )

    # =========================
    # CLEAN PHONE NUMBERS
    # =========================
    if "guardian_contact" in df.columns:

        df["guardian_contact"] = (

            df["guardian_contact"]
            .astype(str)
            .str.replace(".0", "", regex=False)
            .str.strip()
            .str.zfill(10)

        )

    # =========================
    # REMOVE DUPLICATES
    # =========================

    # Remove exact duplicates
    df = df.drop_duplicates()

    # Remove duplicate student IDs
    if "student_id" in df.columns:

        df = df.drop_duplicates(
            subset="student_id",
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
        "profiles_cleaned.csv"
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