"""
DATA SCRAPER - Separate module for downloading stock data
Run this ONCE to download all data, then use cached data in main analysis
"""
import pandas as pd
import yfinance as yf
from datetime import datetime
import os
import json
from pathlib import Path


# Configuration - uses data/ directory
DATA_DIR = Path("data") / "scraped_data"
STATE_FILE = DATA_DIR / "download_state.json"
PRICE_DATA_DIR = DATA_DIR / "prices"


def init_scraper():
    """Initialize scraper directories"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PRICE_DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_download_state():
    """Load download state to track what's already downloaded"""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {'downloaded': {}, 'failed': [], 'last_run': None}


def save_download_state(state):
    """Save download state"""
    state['last_run'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def is_already_downloaded(security_name, state):
    """Check if security data is already downloaded"""
    return security_name in state['downloaded']


def get_price_filename(security_name):
    """Get filename for price data"""
    clean = security_name.replace('/', '_').replace('\\', '_').replace(' ', '_')
    clean = ''.join(c for c in clean if c.isalnum() or c == '_')
    return PRICE_DATA_DIR / f"{clean[:50]}.csv"


def download_stock_data(ticker, start_date, end_date=None):
    """Download data from yfinance"""
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start_date, end=end_date)
        
        if not hist.empty:
            # Remove timezone
            if hasattr(hist.index, 'tz'):
                hist.index = hist.index.tz_localize(None)
            
            # Get monthly data
            monthly = hist['Close'].resample('ME').last()
            return monthly
    except Exception as e:
        return pd.Series()
    
    return pd.Series()


def scrape_all_stocks(ticker_map, start_date, force_redownload=False):
    """
    Main scraping function - downloads all stocks
    Only downloads what's not already cached
    Set force_redownload=True to re-download everything
    """
    init_scraper()
    state = load_download_state()
    
    print("\n" + "="*80)
    print("STOCK DATA SCRAPER")
    print("="*80)
    print(f"\nStart Date: {start_date}")
    print(f"Total Securities to Process: {len(ticker_map)}")
    
    if not force_redownload:
        already_done = sum(1 for sec in ticker_map if is_already_downloaded(sec, state))
        print(f"Already Downloaded: {already_done}")
        print(f"Need to Download: {len(ticker_map) - already_done}")
        
        if already_done == len(ticker_map):
            print("\n✅ All securities already downloaded!")
            print("   Run with force_redownload=True to re-download")
            print("="*80 + "\n")
            return state
    else:
        print("Mode: FORCE RE-DOWNLOAD (ignoring all cache)")
    
    print("\n" + "="*80)
    
    success_count = 0
    failed_count = 0
    skipped_count = 0
    
    for idx, (security_name, ticker) in enumerate(ticker_map.items(), 1):
        # STRICT CHECK: Skip if already downloaded and not forcing
        if not force_redownload:
            if is_already_downloaded(security_name, state):
                filename = get_price_filename(security_name)
                if filename.exists():
                    # File exists and is in state - DEFINITELY skip
                    skipped_count += 1
                    continue
        
        print(f"[{idx:3d}/{len(ticker_map)}] {security_name[:45]:45s} ", end='', flush=True)
        
        # Download data
        data = download_stock_data(ticker, start_date)
        
        if len(data) > 0:
            # Save to file
            filename = get_price_filename(security_name)
            data.to_csv(filename)
            
            # Update state
            state['downloaded'][security_name] = {
                'ticker': ticker,
                'file': str(filename),
                'data_points': len(data),
                'downloaded_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Remove from failed list if it was there
            if security_name in state['failed']:
                state['failed'].remove(security_name)
            
            print(f"✓ ({len(data)} months)")
            success_count += 1
        else:
            # Add to failed list
            if security_name not in state['failed']:
                state['failed'].append(security_name)
            
            print("✗ failed")
            failed_count += 1
        
        # Save state periodically (every 10 downloads)
        if (success_count + failed_count) % 10 == 0:
            save_download_state(state)
    
    # Final state save
    save_download_state(state)
    
    print("\n" + "="*80)
    print("SCRAPING COMPLETE")
    print("="*80)
    print(f"✓ Successfully downloaded: {success_count}")
    print(f"⭐ Skipped (already cached): {skipped_count}")
    print(f"✗ Failed:                   {failed_count}")
    print(f"📂 Data saved to: {PRICE_DATA_DIR}/")
    print(f"📊 State file: {STATE_FILE}")
    print("\nYou can now run main.py to analyze the data!")
    print("="*80 + "\n")
    
    return state


def load_scraped_data():
    """Load all scraped data for analysis"""
    state = load_download_state()
    
    if not state['downloaded']:
        print("❌ No scraped data found! Run data_scraper.py first.")
        return {}
    
    print(f"\n📦 Loading {len(state['downloaded'])} scraped securities...")
    
    stock_data = {}
    success = 0
    failed = 0
    
    for security_name, info in state['downloaded'].items():
        try:
            filename = Path(info['file'])
            
            # Handle both old and new path formats
            if not filename.exists():
                # Try alternative path
                filename = get_price_filename(security_name)
            
            if filename.exists():
                data = pd.read_csv(filename, index_col=0, parse_dates=True)
                
                # Get the Close column or first column
                if 'Close' in data.columns:
                    stock_data[security_name] = data['Close']
                elif len(data.columns) > 0:
                    stock_data[security_name] = data.iloc[:, 0]
                else:
                    failed += 1
                    continue
                
                success += 1
            else:
                failed += 1
                print(f"  ⚠️  File not found: {filename}")
                
        except Exception as e:
            failed += 1
            print(f"  ⚠️  Error loading {security_name}: {e}")
    
    print(f"✓ Loaded {success}/{len(state['downloaded'])} securities from cache")
    
    if failed > 0:
        print(f"⚠️  Failed to load {failed} securities")
    
    print()
    
    return stock_data


def get_scraper_stats():
    """Get statistics about scraped data"""
    state = load_download_state()
    
    stats = {
        'total_downloaded': len(state['downloaded']),
        'total_failed': len(state['failed']),
        'last_run': state.get('last_run', 'Never'),
        'data_dir': str(DATA_DIR)
    }
    
    return stats


if __name__ == "__main__":
    print("\n" + "="*80)
    print("This is the DATA SCRAPER module")
    print("="*80)
    print("\nTo use this module:")
    print("1. Import it in your main script")
    print("2. Call scrape_all_stocks(ticker_map, start_date)")
    print("3. Then use load_scraped_data() to load the data")
    print("\nExample:")
    print("  from data_scraper import scrape_all_stocks, load_scraped_data")
    print("  scrape_all_stocks(ticker_map, '2024-04-01')")
    print("  stock_data = load_scraped_data()")
    print("="*80 + "\n")