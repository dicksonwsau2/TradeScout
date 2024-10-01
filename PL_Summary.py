import sqlite3
import pandas as pd
from datetime import datetime, timedelta  
from db_handler import connect_db, get_trades
from utils import calculate_metrics

# Function to convert the big integer timestamp into human-readable datetime format (forcing 2024 year)
def convert_to_human_readable(bigint_timestamp):  
    unix_time = (bigint_timestamp - 116444736000000000) / 10000000
    return (datetime(1970, 1, 1) + timedelta(seconds=unix_time)).replace(year=2024)

# Add this function to PL_Summary.py

def calculate_premium_captured_over_range(start_date, end_date, connection):
    """
    Calculate the total premium captured over a date range.
    :param start_date: Start date for the range (datetime object)
    :param end_date: End date for the range (datetime object)
    :param connection: Database connection
    :return: Total premium captured over the date range
    """
    current_date = start_date
    total_premium_captured = 0

    while current_date <= end_date:
        # Fetch trades for the current day
        df_trades_ordered = get_trades(connection, current_date.year, current_date.month, current_date.day)
        
        # Calculate metrics for the day
        _, premium_captured, _, _, _, _, _, _, _ = calculate_metrics(df_trades_ordered)
        
        # Sum the premium_captured
        total_premium_captured += premium_captured
        current_date += timedelta(days=1)
    
    return total_premium_captured

# Function to calculate the total PL sum from the last trade of each day between start and end dates
#
# Case 1: Specifying Both Start and End Dates
# total_pl = calculate_total_PL("20240901", "20240923")
# print(f"Total PL from 2024-09-01 to 2024-09-23: {total_pl:.2f}")
#
# Case 2: Specifying Only the Start Date (Defaults End Date to Latest Available Date)
# total_pl = calculate_total_PL("20240901")  # End date defaults to latest available date
# print(f"Total PL from 2024-09-01 to the last available date: {total_pl:.2f}")
def calculate_total_PL(start_date_str, end_date_str=None):
    # Ensure start_date_str is provided
    if not start_date_str:
        raise ValueError("A start date must be provided in the format YYYYMMDD.")

    # Connect to the database using db_handler's connect_db
    try:
        connection = connect_db()
    except ConnectionError as e:
        print(f"Database connection failed: {e}")
        return None

    try:
        # Query to retrieve the DailyLog table
        query = "SELECT DailyLogID, LogDate, PL, SPX FROM DailyLog;"

        # Read the data into a pandas DataFrame
        df_daily_log = pd.read_sql_query(query, connection)

        # Convert LogDate to human-readable format using the updated function
        df_daily_log['LogDate'] = df_daily_log['LogDate'].apply(convert_to_human_readable)

        # Parse the start date
        try:
            start_date = datetime.strptime(start_date_str, "%Y%m%d")
        except ValueError:
            print("Invalid start date format. Please use YYYYMMDD (e.g., 20240917).")
            return None

        # Parse the end date or default to the last available date
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, "%Y%m%d")
            except ValueError:
                print("Invalid end date format. Please use YYYYMMDD (e.g., 20240917).")
                return None
        else:
            end_date = df_daily_log['LogDate'].max()  # Default to latest date in the data

        # Filter the records from start_date to end_date (inclusive)
        df_filtered = df_daily_log[(df_daily_log['LogDate'] >= start_date) & (df_daily_log['LogDate'] <= end_date)]

        # Handle empty data gracefully
        if df_filtered.empty:
            print("No data found for the specified date range.")
            return 0  # Or another appropriate default value

        # Group by the date and pick the last PL entry for each day
        df_last_of_day = df_filtered.groupby(df_filtered['LogDate'].dt.date).tail(1)

        print(f"Calculating total PL from {start_date} to {end_date}")
        print(f"Filtered DataFrame: \n{df_filtered[['LogDate', 'PL']]}")
        print(f"PL values being summed: \n{df_last_of_day[['LogDate', 'PL']]}")

        # Calculate and return the total PL sum from the last trade of each day
        total_pl_sum = df_last_of_day['PL'].sum()

        # Log success of query execution
        print(f"Successfully retrieved PL data. Total PL sum from last trade of each day: {total_pl_sum}")
        return total_pl_sum

    except Exception as e:
        print(f"An error occurred while querying the database: {e}")
        return None
    finally:
        # Ensure the connection is closed
        if connection:
            connection.close()
            print("Database connection closed.")
