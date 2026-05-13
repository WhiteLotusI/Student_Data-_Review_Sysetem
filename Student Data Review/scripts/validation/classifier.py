def classify_dataset(df):
    """
    Classify the dataset type based on expected columns.
    """
    # Define expected columns for each type
    profiles_columns = {
        'student_id', 'student_name', 'class', 'gender', 'guardian_contact'
    }
    performance_columns = {
        'record_id', 'student_id', 'student_name', 'class', 'gender', 'term', 'subject', 
        'attendance_percent', 'assignment_score', 'quiz_score', 
        'exam_score', 'total_score', 'results', 'study_hours', 'teacher_comment'
    }
    attendance_columns = {
        'attendance_id', 'student_id', 'student_name', 'class', 'term', 'days_present', 'days_absent', 
        'total_school_days', 'attendance_percent'
    }

    # Get actual columns in the DataFrame
    columns = set(df.columns)

    # Compare with expected columns
    if columns == profiles_columns:
        return 'profiles'
    elif columns == performance_columns:
        return 'performance'
    elif columns == attendance_columns:
        return 'attendance'
    else:
        raise ValueError("Unknown dataset format: columns don't match expected profiles, performance, or attendance.")