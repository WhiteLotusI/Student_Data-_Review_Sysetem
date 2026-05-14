import os
import traceback

from datetime import datetime


LOG_FOLDER = "scripts/logs"


def log_error(error_message):

    # Create logs folder if it does not exist
    os.makedirs(LOG_FOLDER, exist_ok=True)

    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create log filename
    log_filename = f"error_log_{timestamp}.txt"

    # Full log path
    log_path = os.path.join(LOG_FOLDER, log_filename)

    # Write error into log file
    with open(log_path, "w") as log_file:

        log_file.write(
            "ERROR OCCURRED IN PIPELINE\n"
        )

        log_file.write("=" * 50 + "\n\n")

        log_file.write(error_message)

    print(f"Error logged: {log_filename}")


def validate_file_type(file_path):

    # Extract file extension
    _, file_extension = os.path.splitext(file_path)

    # Check if file is CSV
    if file_extension.lower() != ".csv":

        raise ValueError(
            "Invalid file type. "
            "Only CSV files are supported."
        )


def handle_errors(function_to_run, *args, **kwargs):

    try:

        return function_to_run(*args, **kwargs)

    except Exception as error:

        error_message = (
            f"Exception: {str(error)}\n\n"
        )

        error_message += traceback.format_exc()

        # Log error
        log_error(error_message)

        print("Pipeline failed. Check logs.")

        return None