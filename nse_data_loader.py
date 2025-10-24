"""
Local NSE Data Loader - Uses stock_data_NSE directory instead of scraping
"""
import pandas as pd
import os
from pathlib import Path
from datetime import datetime
import glob

# Directory structure
NSE_DATA_DIR = Path("stock_data_NSE")

def find_stock_file(ticker_symbol):
    """
    Find CSV file for a given ticker in NSE data directory
    ticker_symbol: e.g., 'HDFCBANK.NS' or 'HDFCBANK'
    """
    # Clean ticker - remove .NS/.BO suffix for search
    clean_ticker = ticker_symbol.replace('.NS', '').replace('.BO', '')
    
    # Search pattern
    pattern = f"{clean_ticker}_NS.csv"
    
    # Search in all sector directories
    for sector_dir in NSE_DATA_DIR.iterdir():
        if sector_dir.is_dir():
            file_path = sector_dir / pattern
            if file_path.exists():
                return file_path
    
    return None


def load_stock_data_from_nse(ticker_symbol, start_date):
    """
    Load stock data from local NSE CSV files
    Returns monthly close prices as pandas Series
    """
    file_path = find_stock_file(ticker_symbol)
    
    if not file_path:
        return pd.Series()
    
    try:
        # Read CSV
        df = pd.read_csv(file_path)
        
        # Skip first 2 rows (headers)
        df = df.iloc[2:]
        
        # Reset index
        df = df.reset_index(drop=True)
        
        # Parse date column
        if 'Price' in df.columns:
            df = df.rename(columns={'Price': 'Date'})
        
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')
        
        # Get Close price
        df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
        
        # Filter by start date
        df = df[df.index >= start_date]
        
        # Get monthly last close
        monthly_close = df['Close'].resample('ME').last()
        
        # Remove NaN values
        monthly_close = monthly_close.dropna()
        
        return monthly_close
        
    except Exception as e:
        print(f"Error loading {ticker_symbol}: {e}")
        return pd.Series()


def load_all_nse_data(ticker_map, start_date):
    """
    Load all stock data from NSE directory
    ticker_map: dict of {security_name: ticker_symbol}
    start_date: start date string 'YYYY-MM-DD'
    Returns: dict of {security_name: monthly_close_series}
    """
    stock_data = {}
    success_count = 0
    failed_count = 0
    
    print("\n" + "="*80)
    print("LOADING DATA FROM NSE DIRECTORY")
    print("="*80)
    print(f"Start Date: {start_date}")
    print(f"Total Securities: {len(ticker_map)}")
    print("="*80 + "\n")
    
    for idx, (security_name, ticker) in enumerate(ticker_map.items(), 1):
        print(f"[{idx:3d}/{len(ticker_map)}] {security_name[:50]:50s} ", end='', flush=True)
        
        data = load_stock_data_from_nse(ticker, start_date)
        
        if len(data) > 0:
            stock_data[security_name] = data
            print(f"✓ ({len(data)} months)")
            success_count += 1
        else:
            print("✗ no data")
            failed_count += 1
    
    print("\n" + "="*80)
    print(f"SUCCESS: {success_count}/{len(ticker_map)} securities loaded")
    print(f"FAILED:  {failed_count}/{len(ticker_map)} securities")
    print("="*80 + "\n")
    
    return stock_data


def get_nse_data_stats():
    """Get statistics about available NSE data"""
    total_files = 0
    sector_counts = {}
    
    for sector_dir in NSE_DATA_DIR.iterdir():
        if sector_dir.is_dir():
            files = list(sector_dir.glob("*_NS.csv"))
            count = len(files)
            sector_counts[sector_dir.name] = count
            total_files += count
    
    return {
        'total_files': total_files,
        'sectors': sector_counts
    }


if __name__ == "__main__":
    # Test the loader
    stats = get_nse_data_stats()
    print("\nNSE Data Directory Statistics:")
    print(f"Total CSV files: {stats['total_files']}")
    print("\nBy Sector:")
    for sector, count in sorted(stats['sectors'].items()):
        print(f"  {sector:30s}: {count:4d} files")
    
    # Test loading a stock
    print("\n" + "="*80)
    print("Testing data load for HDFC BANK...")
    data = load_stock_data_from_nse('HDFCBANK.NS', '2024-04-01')
    if len(data) > 0:
        print(f"✓ Loaded {len(data)} data points")
        print("\nSample data:")
        print(data.head())
    else:
        print("✗ Failed to load")
