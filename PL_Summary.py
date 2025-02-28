import pandas as pd
from datetime import datetime, timedelta
import calendar
from db_handler import connect_db, get_trades
from utils import calculate_metrics, convert_to_human_readable

def to_filetime(dt):
    """
    Convert a datetime object to a Windows FILETIME integer.
    FILETIME represents the number of 100-nanosecond intervals since January 1, 1601 (UTC).
    We use the formula:
        filetime = (posix_time * 10,000,000) + 116444736000000000
    """
    posix_time = (dt - datetime(1970, 1, 1)).total_seconds()
    return int(posix_time * 10000000 + 116444736000000000)

def calculate_premium_captured_over_range(start_date, end_date, connection):
    """
    Calculate the total premium captured over a date range.
    
    :param start_date: Start date as a datetime object.
    :param end_date: End date as a datetime object.
    :param connection: An active database connection.
    :return: Total premium captured over the date range.
    """
    current_date = start_date
    total_premium_captured = 0

    while current_date <= end_date:
        df_trades_ordered = get_trades(connection, current_date.year, current_date.month, current_date.day)
        # calculate_metrics returns multiple values; we only need premium_captured here.
        _, premium_captured, _, _, _, _, _, _, _ = calculate_metrics(df_trades_ordered)
        total_premium_captured += premium_captured
        current_date += timedelta(days=1)
    
    return total_premium_captured

def calculate_total_PL(start_date_str, end_date_str=None):
    """
    Calculate the total PL sum from the last trade of each day between start_date_str and end_date_str.
    If end_date_str is omitted, defaults to the current month of the start_date.
    
    This function now only queries data for the specified date range using filetime boundaries,
    which can improve performance when the database contains large amounts of data.
    
    :param start_date_str: Start date in "YYYYMMDD" format.
    :param end_date_str: Optional end date in "YYYYMMDD" format.
    :return: Total PL sum or None if an error occurs.
    """
    if not start_date_str:
        raise ValueError("A start date must be provided in the format YYYYMMDD.")

    try:
        with connect_db() as connection:
            try:
                start_date = datetime.strptime(start_date_str, "%Y%m%d")
            except ValueError:
                print("Invalid start date format. Please use YYYYMMDD (e.g., 20240917).")
                return None

            if end_date_str:
                try:
                    end_date = datetime.strptime(end_date_str, "%Y%m%d")
                except ValueError:
                    print("Invalid end date format. Please use YYYYMMDD (e.g., 20240917).")
                    return None
            else:
                # If end_date is not provided, limit to the current month of the start_date.
                end_date = start_date.replace(day=calendar.monthrange(start_date.year, start_date.month)[1])

            # Compute the filetime boundaries for the given date range.
            start_filetime = to_filetime(start_date)
            # To get the end of the day for end_date, add one day and subtract 1.
            end_filetime = to_filetime(end_date + timedelta(days=1)) - 1

            # Query only rows with LogDate within the filetime boundaries.
            query = "SELECT DailyLogID, LogDate, PL, SPX FROM DailyLog WHERE LogDate BETWEEN ? AND ?;"
            df_daily_log = pd.read_sql_query(query, connection, params=(start_filetime, end_filetime))

            # Convert LogDate from filetime to a human-readable date.
            df_daily_log['LogDate'] = df_daily_log['LogDate'].apply(convert_to_human_readable)

            if df_daily_log.empty:
                print("No data found for the specified date range.")
                return 0

            # Group by date (using the human-readable LogDate) and pick the last entry of each day.
            df_last_of_day = df_daily_log.groupby(df_daily_log['LogDate'].dt.date).tail(1)

            print(f"Calculating total PL from {start_date} to {end_date}")
            print(f"Filtered DataFrame:\n{df_daily_log[['LogDate', 'PL']]}")
            print(f"PL values being summed:\n{df_last_of_day[['LogDate', 'PL']]}")

            total_pl_sum = df_last_of_day['PL'].sum()
            print(f"Total PL sum: {total_pl_sum}")
            return total_pl_sum

    except Exception as e:
        print(f"An error occurred while querying the database: {e}")
        return None
