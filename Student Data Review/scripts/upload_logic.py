from pathlib import Path
import shutil
from datetime import datetime


# =========================================
# PROJECT PATHS
# =========================================

ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = ROOT / "data" / "raw"

# Create raw folder if it does not exist
RAW_DIR.mkdir(parents=True, exist_ok=True)


def upload_file():

    # =====================================
    # GET FILE PATH FROM USER
    # =====================================

    user_file_path = input(
        "\nEnter CSV file path: "
    ).strip()

    # Convert to Path object
    source_path = Path(user_file_path)

    # =====================================
    # CHECK FILE EXISTS
    # =====================================

    if not source_path.exists():

        raise FileNotFoundError(
            f"File not found:\n{source_path}"
        )

    # =====================================
    # VALIDATE FILE TYPE
    # =====================================

    if source_path.suffix.lower() != ".csv":

        raise ValueError(
            "Invalid file type. "
            "Only CSV files are supported."
        )

    # =====================================
    # GENERATE CLEAN FILE NAME
    # =====================================

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    clean_name = (
        f"{source_path.stem}_{timestamp}.csv"
    )

    # =====================================
    # DESTINATION PATH
    # =====================================

    destination_path = (
        RAW_DIR / clean_name
    )

    # =====================================
    # COPY FILE TO RAW FOLDER
    # =====================================

    shutil.copy2(
        source_path,
        destination_path
    )

    print(
        "\nFile uploaded successfully."
    )

    print(
        f"Saved to:\n{destination_path}"
    )

    # =====================================
    # RETURN SAVED FILE PATH
    # =====================================

    return destination_path