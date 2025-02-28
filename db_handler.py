import sqlite3
import pandas as pd
import yaml
import os
import time
from datetime import datetime
from utils import convert_to_human_readable, load_yaml_config
import sys
from contextlib import contextmanager

# Load YAML configuration
def load_config():
    return load_yaml_config()

@contextmanager
def connect_db(retries=5, delay=1):
    """
    Context manager to connect to the SQLite database with optional retries.
    Usage:
        with connect_db() as connection:
            # use 'connection' here
    """
    config = load_config()
    db_path = config.get('db_path', 'data/data.db3')

    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found at {db_path}")

    connection = None
    for attempt in range(retries):
        try:
            connection = sqlite3.connect(db_path)
            print(f"Connected to the database at {db_path} on attempt {attempt + 1}.")
            break
        except sqlite3.OperationalError as e:
            print(f"Attempt {attempt + 1} of {retries} failed: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise ConnectionError(f"Failed to connect after {retries} attempts") from e

    try:
        yield connection
    finally:
        if connection:
            connection.close()
            print("Database connection closed.")

def get_trades(connection, year, month, day):
    """
    Retrieve trades for the specified date and return a DataFrame with columns
    in a consistent order.
    """
    query = f"""
    SELECT
        TradeID, DateOpened, DateClosed, TradeType,
        ShortPut, LongPut, ShortCall, LongCall,
        Qty, StopType, PriceOpen, PriceStopTarget,
        ProfitLoss, PriceClose, ClosingProcessed,
        TotalPremium, Commission, CommissionClose
    FROM Trade
    WHERE Year = {year}
      AND Month = {month}
      AND Day = {day}
      AND TATTradeID IS NOT NULL;
    """
    df_trades = pd.read_sql_query(query, connection)

    # Convert date fields
    df_trades['DateOpened'] = df_trades['DateOpened'].apply(convert_to_human_readable)
    df_trades['DateClosed'] = df_trades['DateClosed'].apply(convert_to_human_readable)

    # Reorder columns for consistency
    df_trades_ordered = df_trades[[
        "TradeID", "DateOpened", "TradeType", "ShortPut", "LongPut",
        "ShortCall", "LongCall", "Qty", "StopType", "PriceOpen",
        "PriceStopTarget", "ProfitLoss", "PriceClose", "DateClosed",
        "ClosingProcessed", "TotalPremium", "Commission", "CommissionClose"
    ]]
    
    return df_trades_ordered
