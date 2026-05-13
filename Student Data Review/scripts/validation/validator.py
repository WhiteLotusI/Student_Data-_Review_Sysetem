import os
from datetime import datetime


LOG_FOLDER = "scripts/logs"


def create_log_file(dataset_type, validation_report):

    # Create logs folder if it does not exist
    os.makedirs(LOG_FOLDER, exist_ok=True)

    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create log filename
    log_filename = f"{dataset_type}_validation_log_{timestamp}.txt"

    # Full log path
    log_path = os.path.join(LOG_FOLDER, log_filename)

    # Write validation report into text file
    with open(log_path, "w") as log_file:

        log_file.write(
            f"{dataset_type.upper()} VALIDATION REPORT\n"
        )

        log_file.write("=" * 50 + "\n\n")

        for issue in validation_report:
            log_file.write(f"- {issue}\n")

    print(f"Validation log created: {log_filename}")


def validate_profiles(df):

    validation_report = []

    required_columns = {
        "student_id",
        "student_name",
        "class",
        "gender",
        "guardian_contact"
    }

    # Check missing columns
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        validation_report.append(
            f"Missing Columns: {missing_columns}"
        )

    # Check null values
    for column in required_columns:

        if column in df.columns:

            null_count = df[column].isnull().sum()

            if null_count > 0:

                validation_report.append(
                    f"{column} has {null_count} missing values"
                )

    # Check duplicate student IDs
    if "student_id" in df.columns:

        duplicate_count = (
            df["student_id"]
            .duplicated()
            .sum()
        )

        if duplicate_count > 0:

            validation_report.append(
                f"Found {duplicate_count} duplicate student IDs"
            )

    # Create log file
    create_log_file("profiles", validation_report)

    return validation_report


def validate_performance(df):

    validation_report = []

    required_columns = {
        "record_id",
        "student_id",
        "student_name",
        "class",
        "gender",
        "term",
        "subject",
        "attendance_percent",
        "assignment_score",
        "quiz_score",
        "exam_score",
        "total_score",
        "results",
        "study_hours",
        "teacher_comment"
    }

    # Check missing columns
    missing_columns = required_columns - set(df.columns)

    if missing_columns:

        validation_report.append(
            f"Missing Columns: {missing_columns}"
        )

    # Check null values
    for column in required_columns:

        if column in df.columns:

            null_count = df[column].isnull().sum()

            if null_count > 0:

                validation_report.append(
                    f"{column} has {null_count} missing values"
                )

    # Check duplicate record IDs
    if "record_id" in df.columns:

        duplicate_count = (
            df["record_id"]
            .duplicated()
            .sum()
        )

        if duplicate_count > 0:

            validation_report.append(
                f"Found {duplicate_count} duplicate record IDs"
            )

    # Validate score ranges
    score_columns = [
        "assignment_score",
        "quiz_score",
        "exam_score",
        "total_score",
        "attendance_percent"
    ]

    for column in score_columns:

        if column in df.columns:

            invalid_scores = (
                (df[column] < 0) |
                (df[column] > 100)
            ).sum()

            if invalid_scores > 0:

                validation_report.append(
                    f"{column} has "
                    f"{invalid_scores} invalid values "
                    f"(outside 0-100 range)"
                )

    # Create log file
    create_log_file("performance", validation_report)

    return validation_report


def validate_attendance(df):

    validation_report = []

    required_columns = {
        "attendance_id",
        "student_id",
        "student_name",
        "class",
        "term",
        "days_present",
        "days_absent",
        "total_school_days",
        "attendance_percent"
    }

    # Check missing columns
    missing_columns = required_columns - set(df.columns)

    if missing_columns:

        validation_report.append(
            f"Missing Columns: {missing_columns}"
        )

    # Check null values
    for column in required_columns:

        if column in df.columns:

            null_count = df[column].isnull().sum()

            if null_count > 0:

                validation_report.append(
                    f"{column} has {null_count} missing values"
                )

    # Check duplicate attendance IDs
    if "attendance_id" in df.columns:

        duplicate_count = (
            df["attendance_id"]
            .duplicated()
            .sum()
        )

        if duplicate_count > 0:

            validation_report.append(
                f"Found {duplicate_count} duplicate attendance IDs"
            )

    # Validate attendance percent
    if "attendance_percent" in df.columns:

        invalid_attendance = (
            (df["attendance_percent"] < 0) |
            (df["attendance_percent"] > 100)
        ).sum()

        if invalid_attendance > 0:

            validation_report.append(
                f"attendance_percent has "
                f"{invalid_attendance} invalid values"
            )

    # Create log file
    create_log_file("attendance", validation_report)

    return validation_report