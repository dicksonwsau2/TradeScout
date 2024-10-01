import sys
import os
import sqlite3

# Add the parent directory (where utils.py and db_handler.py are located) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import get_last_spx_value  # Import the function from utils
from db_handler import load_config, connect_db  # Import the functions from db_handler

def test_spx_values():
    # Load configuration to get the database path
    config = load_config()
    
    # Connect to the database with retries
    connection = connect_db(retries=5, delay=1)
    
    # Dates to test
    dates_to_test = [
        (2024, 9, 23),
        (2024, 9, 24),
        (2024, 9, 25),
        (2024, 9, 26)
    ]
    
    # Iterate through the dates and fetch the last SPX value for each day
    for year, month, day in dates_to_test:
        spx_last = get_last_spx_value(connection, year, month, day)
        if spx_last is not None:
            print(f"Last SPX value for {year}-{month:02d}-{day:02d}: {spx_last}")
        else:
            print(f"No SPX value found for {year}-{month:02d}-{day:02d}")

    # Close the connection to the database
    connection.close()

if __name__ == "__main__":
    test_spx_values()
