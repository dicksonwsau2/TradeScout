import os
import sys
import yaml
import pandas as pd  
import sqlite3 
import pygetwindow as gw
import pyautogui
from datetime import datetime, timedelta
import threading 
import calendar
from io import BytesIO
import tempfile

def load_yaml_config():
    """
    Load the YAML configuration file from the correct path based on whether
    the program is running as a script or as an executable.
    """
    if hasattr(sys, '_MEIPASS'):
        # If running as an executable, load from the same directory as the executable
        config_path = os.path.join(os.path.dirname(sys.executable), 'config.yaml')
    else:
        # If running as a script, load from the 'config' folder at the same level as the script
        script_dir = os.path.dirname(__file__)
        config_path = os.path.join(script_dir, 'config', 'config.yaml')

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at {config_path}")

    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def take_screenshot_of_app(app_name, win):
    try:
        app_window = gw.getWindowsWithTitle(app_name)[0]
    except IndexError:
        print(f"Application window '{app_name}' not found.")
        return None

    # Handle window adjustment
    if win == 'max' and not app_window.isMaximized:
        app_window.maximize()
    elif win == 'restore' and app_window.isMinimized:
        app_window.restore()

    app_window.activate()
    pyautogui.sleep(2)

    # Take the screenshot
    screenshot = pyautogui.screenshot(region=(app_window.left, app_window.top, app_window.width, app_window.height))

    # Save the screenshot to a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    screenshot.save(temp_file.name)
    temp_file.close()

    return temp_file.name  # Return the path of the temporary screenshot file

def convert_to_human_readable(bigint_timestamp):
    unix_time = (bigint_timestamp - 116444736000000000) / 10000000
    return (datetime(1970, 1, 1) + timedelta(seconds=unix_time)).replace(year=2024)

def get_most_recent_monday(date):
    days_ago = (date.weekday() + 1) % 7
    return date - timedelta(days=days_ago)

def get_specified_date(date_str=None):
    """
    Converts a date string to a datetime object or returns the current datetime.
    If no date string is provided, the current date is returned.
    """
    if date_str:
        return datetime.strptime(date_str, "%Y%m%d")
    else:
        # Return the current date and time if no date string is provided
        return datetime.now()

def format_message(date, premium_sold, premium_captured, pcr, win_rate, expired_trades, stops, bad_slip, bad_slip_max, spx_last, negative_exp, weekly_pl, monthly_pl):
    # Define a constant for alignment width
    ALIGN_WIDTH = 11

    # Format values as strings with proper formatting
    premium_sold_str = f"${premium_sold:,.2f}"
    premium_captured_str = f"(${abs(premium_captured):,.2f})" if premium_captured < 0 else f"${premium_captured:,.2f}"
    pcr_str = f"{pcr:.2f}%"  # Format as percentage with two decimal places
    win_rate_str = f"{win_rate:.2f}%"  # Format as percentage with two decimal places
    exp_stp_str = f"{expired_trades}:{stops}"  # Expired trades and stops as a ratio
    bad_slip_str = f"{int(bad_slip):,}"  # Format bad slip as an integer with commas
    bad_slip_max_str = f"{abs(bad_slip_max):,.2f}" if bad_slip_max is not None else ""  
    spx_last_str = f"{spx_last:,.2f}" if spx_last is not None else ""
    
    # Combine bad_slip and bad_slip_max and ensure the total length fits within the column width
    combined_bad_slip_str = f"{bad_slip_str}({bad_slip_max_str} max)" if bad_slip_max else bad_slip_str
    bad_slip_combined_str = f"{combined_bad_slip_str:>{ALIGN_WIDTH}}"  # Right-align the combined string within the specified width

    negative_exp_str = f"{negative_exp}"  
    weekly_pl_str = f"(${abs(weekly_pl):,.2f})" if weekly_pl < 0 else f"${weekly_pl:,.2f}"
    monthly_pl_str = f"(${abs(monthly_pl):,.2f})" if monthly_pl < 0 else f"${monthly_pl:,.2f}"

    # Create the formatted message
    formatted_date = date.strftime("%Y %b %d")
    day_of_week = calendar.day_name[date.weekday()]
    full_date_header = f"{formatted_date} ({day_of_week})"
    
    message = f"""
\n
""" + "```" + f"""
{full_date_header}
----------|------------
SPX Last  | {spx_last_str:>{ALIGN_WIDTH}}
Prem Sold | {premium_sold_str:>{ALIGN_WIDTH}}
Prem Cap  | {premium_captured_str:>{ALIGN_WIDTH}}
PCR       | {pcr_str:>{ALIGN_WIDTH}}
Win %     | {win_rate_str:>{ALIGN_WIDTH}}
Exp : Stp | {exp_stp_str:>{ALIGN_WIDTH}}
Bad Slip  | {bad_slip_combined_str:>{ALIGN_WIDTH}}
-ve Exprd | {negative_exp_str:>{ALIGN_WIDTH}}
WTD PL    | {weekly_pl_str:>{ALIGN_WIDTH}}
MTD PL    | {monthly_pl_str:>{ALIGN_WIDTH}}
""" + "```"
    return message

def calculate_metrics(df_trades_ordered):
    premium_sold = df_trades_ordered['TotalPremium'].sum()
    premium_captured = df_trades_ordered['ProfitLoss'].sum()
    
    # Calculate pcr, win_rate based on whether premium_sold is zero
    pcr, win_rate = (
        ((premium_captured / premium_sold) * 100, 
        (df_trades_ordered['ProfitLoss'] > 0).mean() * 100) 
        if premium_sold != 0 else (0, 0)
    )
    
    expired_trades = (df_trades_ordered['ClosingProcessed'] == 0).sum()
    stops = (df_trades_ordered['ClosingProcessed'] == 1).sum()

    # Calculate both bad_slip and bad_slip_max in one pass
    bad_slip_data = df_trades_ordered.apply(
        lambda row: abs(row['PriceClose']) - row['PriceStopTarget'], axis=1
    )

    # Find bad slips where the difference is >= 0.50
    bad_slip_condition = bad_slip_data >= 0.50
    
    bad_slip = bad_slip_condition.sum()  # Count how many satisfy the condition
    bad_slip_max = bad_slip_data[bad_slip_condition].max() if bad_slip > 0 else 0  # Max of valid slips, or 0 if none

    negative_exp = df_trades_ordered[
        (df_trades_ordered['ClosingProcessed'] == 0) & 
        (df_trades_ordered['ProfitLoss'] < 0)
    ].shape[0]
 
    # Return the calculated metrics including bad_slip_max and spx_last
    return premium_sold, premium_captured, pcr, win_rate, expired_trades, stops, bad_slip, bad_slip_max, negative_exp

def input_with_timeout(prompt, timeout):
    answer = [None]
    
    def get_input():
        answer[0] = input(prompt)
    
    thread = threading.Thread(target=get_input)
    thread.start()
    thread.join(timeout)
    
    if thread.is_alive():  # Timeout handling
        print("\nNo response received. The posting will not be deleted.")
        return None
    else:
        return answer[0]

def get_last_spx_value(connection, year, month, day):
    """
    Retrieve the last SPX value for a given day from the DailyLog table and print the DailyLogID, PL, and SPX.
    
    :param connection: SQLite database connection
    :param year: Year of the date to query
    :param month: Month of the date to query
    :param day: Day of the date to query
    :return: The last SPX value for the day, or None if no entries are found
    """
    try:
        # Create a datetime object for the target date
        target_date = datetime(year, month, day)
        
        # SQL query to fetch all entries from the DailyLog table
        query = "SELECT DailyLogID, LogDate, PL, SPX FROM DailyLog WHERE LogDate IS NOT NULL;"
                
        # Fetch the data from the DailyLog table
        df_daily_log = pd.read_sql_query(query, connection)
        
        # Convert LogDate to human-readable format using convert_to_human_readable
        df_daily_log['LogDate'] = df_daily_log['LogDate'].apply(convert_to_human_readable)
        
        # Filter the DataFrame to only include entries matching the target date
        df_filtered = df_daily_log[df_daily_log['LogDate'].dt.date == target_date.date()]
        
        if not df_filtered.empty:
            # Get the last SPX value of the day
            last_spx_value = df_filtered.iloc[-1]['SPX']
            print(f"Last SPX value found: {last_spx_value}")
            return last_spx_value
        else:
            print(f"No SPX value found for {target_date.strftime('%Y-%m-%d')}")
            return None

    except sqlite3.Error as e:
        print(f"Database error occurred: {e}")
        return None