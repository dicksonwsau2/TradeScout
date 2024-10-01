import argparse
from datetime import datetime, timedelta
from db_handler import get_trades, connect_db
from discord_messenger import send_message_to_discord, delete_messages
from utils import input_with_timeout, get_specified_date, calculate_metrics, format_message, get_most_recent_monday, get_last_spx_value
from PL_Summary import calculate_premium_captured_over_range  

# Argument parser for command line parameters
parser = argparse.ArgumentParser(description='Process trades and send updates.')
parser.add_argument('--noimage', action='store_true', help='Disable image capture and sending to webhook.')
parser.add_argument('--date', type=str, nargs='?', const=None, help='Specify a date in the format YYYYMMDD (e.g., 20240920). If omitted, current date is used.')
parser.add_argument('--debug', action='store_true', help='Print message to console and save image to file.')
parser.add_argument('--win', type=str, choices=['max', 'restore'], help='Adjust window size before screenshot: "max" to maximize, "restore" to restore.')
args = parser.parse_args()

# Get current date or specified date
specified_date = get_specified_date(args.date)
year, month, day = specified_date.year, specified_date.month, specified_date.day

# Connect to database
connection = connect_db()

# Calculate Weekly PL (Sum of premium_captured from most_recent_monday to specified_date)
most_recent_monday = get_most_recent_monday(specified_date)
weekly_pl = calculate_premium_captured_over_range(most_recent_monday, specified_date, connection)

# Calculate Monthly PL (Sum of premium_captured from first_day_of_month to specified_date)
first_day_of_month = specified_date.replace(day=1)
monthly_pl = calculate_premium_captured_over_range(first_day_of_month, specified_date, connection)

# Fetch trades for the specified date and calculate daily metrics
df_trades_ordered = get_trades(connection, year, month, day)
premium_sold, premium_captured, pcr, win_rate, expired_trades, stops, bad_slip, bad_slip_max, negative_exp = calculate_metrics(df_trades_ordered)

spx_last = get_last_spx_value(connection, year, month, day)

# Format message and include weekly and monthly PL
formatted_message = format_message(specified_date, premium_sold, premium_captured, pcr, win_rate, expired_trades, stops, bad_slip, bad_slip_max, spx_last, negative_exp, weekly_pl, monthly_pl)

# Send the message and handle images
message_ids = send_message_to_discord(formatted_message, args.noimage, args.win, args.debug)

# Option to delete messages after sending
user_input = input_with_timeout("Do you want to delete the posting? (Y/N): ", 30)
if user_input and user_input.strip().lower() in ['yes', 'y']:
    delete_messages(message_ids)

# Close the database connection
connection.close()
