import sqlite3
import pandas as pd  
import yaml
import os
import time
from datetime import datetime
from utils import convert_to_human_readable 

# Load YAML configuration
def load_config():
    # Resolve the config path relative to the current file (which is inside TradeScout)
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.yaml')
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at {config_path}")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

# Connect to the database using the db_path from config.yaml
# Connect to the database with retry logic
def connect_db(retries=5, delay=1):
    config = load_config()
    
    # Resolve the db_path relative to the TradeScout project directory
    tradescout_root = os.path.dirname(__file__)  # Use this as the root directory
    db_path = os.path.join(tradescout_root, config.get('db_path', 'data/data.db3'))  # Default path if not found in config

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


