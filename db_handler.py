import sqlite3
import pandas as pd  
import yaml
import os
import time
from datetime import datetime
from utils import convert_to_human_readable, load_yaml_config
import sys

# Load YAML configuration
def load_config():
    return load_yaml_config()

# Connect to the database using the db_path from config.yaml
def connect_db(retries=5, delay=1):
    config = load_config()
    
    # Use the database path from config.yaml
    db_path = config.get('db_path', 'data/data.db3')

    # Check if the database file exists
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found at {db_path}")

    # Retry logic for connecting to the database
    for attempt in range(retries):
        try:
            connection = sqlite3.connect(db_path)
            print(f"Connected to the database at {db_path} on attempt {attempt + 1}.")
            return connection
        except sqlite3.OperationalError as e:
            print(f"Attempt {attempt + 1} of {retries} to connect to the database failed: {e}")
            if attempt < retries - 1:
                time.sleep(delay)  # Wait before retrying
            else:
                raise ConnectionError(f"Failed to connect to the database after {retries} attempts") from e

def get_trades(connection, year, month, day):
    query = f"""
    SELECT TradeID, DateOpened, DateClosed, TradeType, ShortPut, LongPut, ShortCall, LongCall, 
           Qty, StopType, PriceOpen, PriceStopTarget, ProfitLoss, PriceClose, 
           ClosingProcessed, TotalPremium, Commission, CommissionClose
    FROM Trade
    WHERE Year = {year} 
    AND Month = {month} 
    AND Day = {day}
    AND TATTradeID IS NOT NULL;
    """
    df_trades = pd.read_sql_query(query, connection)

    # Convert dates
    df_trades['DateOpened'] = df_trades['DateOpened'].apply(convert_to_human_readable)
    df_trades['DateClosed'] = df_trades['DateClosed'].apply(convert_to_human_readable)

    # Reorder columns
    df_trades_ordered = df_trades[[
        "TradeID", "DateOpened", "TradeType", "ShortPut", "LongPut", "ShortCall", "LongCall", 
        "Qty", "StopType", "PriceOpen", "PriceStopTarget", "ProfitLoss", "PriceClose", 
        "DateClosed", "ClosingProcessed", "TotalPremium", "Commission", "CommissionClose"
    ]]
    
    return df_trades_ordered


