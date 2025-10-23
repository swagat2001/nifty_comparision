"""
Module for fetching REAL market data - NO PROXY DATA
"""
import yfinance as yf
import pandas as pd
from datetime import datetime
from config import INVESTMENT_DATE
import os


def get_nse_symbol(security_name):
    """Convert security name to NSE symbol for yfinance"""
    # Clean the security name
    name = str(security_name).upper()
    
    # Extract ticker from security name
    # Format: "COMPANY NAME LIMITED EQ" -> "COMPANY"
    name = name.replace(' LIMITED', '').replace(' LTD', '')
    name = name.replace(' EQ NEW', '').replace(' EQ', '')
    name = name.replace(' NEW RS. 2/-', '').replace(' RS. 10/-', '')
    name = name.replace(' RS. 2/', '').replace(' RS. 10/', '')
    name = name.strip()
    
    # Add .NS for NSE
    return f"{name}.NS"


def fetch_stock_historical_data(symbol, start_date, end_date=None):
    """
    Fetch real historical data for a stock from Yahoo Finance
    """
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(start=start_date, end=end_date)
        
        if not hist.empty:
            # Get monthly closing prices
            monthly = hist['Close'].resample('ME').last()
            return monthly
        else:
            return pd.Series()
    except Exception as e:
        return pd.Series()


def fetch_nifty_data(start_date, end_date=None):
    """Fetch NIFTY indices data"""
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    nifty_symbols = {
        "NIFTY 50": "^NSEI",
        "NIFTY Midcap 100": "^NSEMDCP50",
        "NIFTY 100": "^CNX100"
    }
    
    nifty_data = {}
    
    for name, symbol in nifty_symbols.items():
        try:
            print(f"  Fetching {name}...")
            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date)
            
            if not hist.empty:
                monthly = hist['Close'].resample('ME').last()
                nifty_data[name] = monthly
        except Exception as e:
            print(f"  ⚠ Failed to fetch {name}: {e}")
    
    return nifty_data


def save_to_csv(data, filename, folder='data_cache'):
    """Save data to CSV for caching"""
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)
    data.to_csv(filepath)
    return filepath


def load_from_csv(filename, folder='data_cache'):
    """Load cached data from CSV"""
    filepath = os.path.join(folder, filename)
    if os.path.exists(filepath):
        return pd.read_csv(filepath, index_col=0, parse_dates=True)
    return None
