"""
Smart Ticker Resolver - Finds working tickers with multiple fallback strategies
"""
import pandas as pd
import yfinance as yf
from datetime import datetime
import time
import os
from validated_tickers import VALIDATED_NSE_TICKERS, get_validated_ticker


# Comprehensive NSE ticker mapping - COMPLETE DATABASE
NSE_TICKER_MAP = {
    # Major Companies
    'ADANI PORTS AND SPECIAL ECONOMIC ZONE LIMITED': 'ADANIPORTS',
    'ASIAN PAINTS LIMITED': 'ASIANPAINT',
    'BHARTI AIRTEL LIMITED': 'BHARTIARTL',
    'COAL INDIA LTD': 'COALINDIA',
    'HDFC BANK LIMITED': 'HDFCBANK',
    'HINDUSTAN UNILEVER LIMITED': 'HINDUNILVR',
    'INFOSYS LIMITED': 'INFY',
    'LARSEN AND TOUBRO LIMITED': 'LT',
    'LARSEN & TOUBRO LIMITED': 'LT',
    'RELIANCE INDUSTRIES LIMITED': 'RELIANCE',
    'RELIANCE POWER LIMITED': 'RPOWER',
    'TATA CONSULTANCY SERVICES LIMITED': 'TCS',
    'TATA STEEL LIMITED': 'TATASTEEL',
    
    # Failed ones from your log - CORRECT MAPPINGS
    'CG POWER AND INDUSTRIAL SOLUTIONS LIMITED': 'CGPOWER',
    'CHAMBAL FERTILISERS AND CHEMICALS LIMITED': 'CHAMBLFERT',
    'CROMPTON GREAVES CONSUMER ELECTRICALS LIMITED': 'CROMPTON',
    'DABUR INDIA LIMITED': 'DABUR',
    'ENERGY DEVELOPMENT COMPANY LIMITED': 'ENERGYDEV',
    'IFCI LIMITED': 'IFCI',
    'JAI CORP LIMITED': 'JAICORPLTD',
    'JAIPRAKASH ASSOCIATES LIMITED': 'JPASSOCIAT',
    'JAY SHREE TEA AND INDUSTRIES LIMITED': 'JAYSREETEA',
    'JINDAL STEEL LIMITED': 'JSL',
    'JIO FINANCIAL SERVICES LIMITED': 'JIOFIN',
    'LTIMINDTREE LIMITED': 'LTIM',
    'PAE LIMITED': 'PAELIMITED',
    'POWER GRID CORPORATION OF INDIA LIMITED': 'POWERGRID',
    
    # Banking & Finance
    'BAJAJ FINANCE LIMITED': 'BAJFINANCE',
    'REC LIMITED': 'RECLTD',
    'SBI CARDS AND PAYMENT SERVICES LIMITED': 'SBICARD',
    'LIC HOUSING FINANCE LTD': 'LICHSGFIN',
    'AXIS BANK LIMITED': 'AXISBANK',
    'ICICI BANK LIMITED': 'ICICIBANK',
    'STATE BANK OF INDIA': 'SBIN',
    
    # Utilities
    'GUJARAT STATE PETRONET LIMITED': 'GSPL',
    'TORRENT POWER LIMITED': 'TORNTPOWER',
    'HPL ELECTRIC & POWER LIMITED': 'HPL',
    'TATA POWER COMPANY LIMITED': 'TATAPOWER',
    'NTPC LIMITED': 'NTPC',
    
    # Oil & Gas
    'MANGALORE REFINERY AND PETROCHEMICALS LIMITED': 'MRPL',
    'OIL AND NATURAL GAS CORPORATION LIMITED': 'ONGC',
    'INDIAN OIL CORPORATION LIMITED': 'IOC',
    'BHARAT PETROLEUM CORPORATION LIMITED': 'BPCL',
    
    # IT & Tech
    'KHADIM INDIA LIMITED': 'KHADIM',
    'WIPRO LIMITED': 'WIPRO',
    'TECH MAHINDRA LIMITED': 'TECHM',
    'HCL TECHNOLOGIES LIMITED': 'HCLTECH',
    
    # Pharma
    'AUROBINDO PHARMA': 'AUROPHARMA',
    'BIOCON LIMITED': 'BIOCON',
    'MANKIND PHARMA LTD': 'MANKIND',
    'GLENMARK PHARMACEUTICALS LTD': 'GLENMARK',
    'DR REDDY\'S LABORATORIES LIMITED': 'DRREDDY',
    'CIPLA LIMITED': 'CIPLA',
    'SUN PHARMACEUTICAL INDUSTRIES LIMITED': 'SUNPHARMA',
    
    # Manufacturing
    'ESCORTS KUBOTA LIMITED': 'ESCORTS',
    'EXIDE INDUSTRIES LIMITED': 'EXIDEIND',
    'BASF INDIA LTD': 'BASF',
    'CONTAINER CORPORATION OF INDIA': 'CONCOR',
    'CUMMINS INDIA LIMITED': 'CUMMINSIND',
    'BHARAT ELECTRONICS LIMITED': 'BEL',
    'BHARAT HEAVY ELECTRICALS LIMITED': 'BHEL',
    
    # Auto
    'MARUTI SUZUKI INDIA LIMITED': 'MARUTI',
    'TATA MOTORS LIMITED': 'TATAMOTORS',
    'MAHINDRA & MAHINDRA LIMITED': 'M&M',
    'BAJAJ AUTO LIMITED': 'BAJAJ-AUTO',
    'HERO MOTOCORP LIMITED': 'HEROMOTOCO',
    
    # Real Estate
    'PIX TRANSMISSIONS LIMITED': 'PIXTRANS',
    'PURAVANKARA LIMITED': 'PURVA',
    'DLF LIMITED': 'DLF',
    'GODREJ PROPERTIES LIMITED': 'GODREJPROP',
    
    # FMCG
    'ITC LIMITED': 'ITC',
    'BRITANNIA INDUSTRIES LIMITED': 'BRITANNIA',
    'NESTLE INDIA LIMITED': 'NESTLEIND',
    
    # Textiles
    'ADITYA BIRLA FASHION AND RETAIL LIMITED': 'ABFRL',
    
    # Others
    'TATA TECHNOLOGIES LTD': 'TATATECH',
    'SYNGENE INTERNATIONAL LTD': 'SYNGENE',
    'RATTANINDIA ENTERPRISES': 'RTNINDIA',
    'INDEGENE LTD': 'INDGN',
    'NAZARA TECHNOLOGIES LTD': 'NAZARA',
    'POLICYBAZAAR': 'POLICYBZR',
    'MTAR TECHNOLOGIES LTD': 'MTARTECH',
    'WEST COAST PAPER MILLS LIMITED': 'WSTCSTPAPR',
    'ATUL LIMITED': 'ATUL',
    'ANIL LIMITED': 'ANILLTD',
}


def clean_security_name(name):
    """Clean and standardize security name"""
    clean = str(name).upper().strip()
    clean = clean.replace(' EQ NEW RS. 2/-', '').replace(' EQ NEW RS. 2/', '')
    clean = clean.replace(' EQ NEW FV RS. 2/-', '').replace(' EQ NEW', '')
    clean = clean.replace(' RS. 10/-', '').replace(' RS. 2/-', '')
    clean = clean.replace(' EQ', '').replace(' NEW', '')
    clean = clean.replace(' FV RS. 10/-', '').replace(' FV RS. 2/-', '')
    clean = clean.replace(' 10/-', '').replace(' 2/-', '')
    return clean.strip()


def try_ticker_variations(base_name):
    """Generate multiple ticker variations to try"""
    variations = []
    
    # Try exact match from map
    if base_name in NSE_TICKER_MAP:
        variations.append(NSE_TICKER_MAP[base_name] + '.NS')
        variations.append(NSE_TICKER_MAP[base_name] + '.BO')
    
    # Extract first word
    words = base_name.split()
    if words:
        first_word = words[0]
        variations.append(first_word + '.NS')
        variations.append(first_word + '.BO')
        
        # Try first two words combined
        if len(words) > 1:
            combined = words[0] + words[1]
            variations.append(combined + '.NS')
            variations.append(combined + '.BO')
    
    # Try abbreviated form
    if ' LIMITED' in base_name or ' LTD' in base_name:
        abbrev = base_name.replace(' LIMITED', '').replace(' LTD', '')
        abbrev = ''.join(w[0] for w in abbrev.split() if w)
        if len(abbrev) > 2:
            variations.append(abbrev + '.NS')
            variations.append(abbrev + '.BO')
    
    return list(dict.fromkeys(variations))  # Remove duplicates


def test_ticker(ticker, start_date, quick_test=True):
    """Test if a ticker returns valid data"""
    try:
        stock = yf.Ticker(ticker)
        if quick_test:
            # Quick test - just check info
            info = stock.info
            if info and 'regularMarketPrice' in info:
                return True
        else:
            # Full test - fetch historical data
            hist = stock.history(start=start_date, period='1mo')
            if not hist.empty and len(hist) > 0:
                return True
    except Exception as e:
        # Don't print errors during testing
        pass
    return False


def find_working_ticker(security_name, start_date):
    """Find a working ticker for a security with multiple attempts"""
    # Try validated database first (only confirmed working tickers)
    ticker = get_validated_ticker(security_name)
    if ticker:
        if test_ticker(ticker, start_date, quick_test=False):
            return ticker
    
    # Fallback to variations (but less likely to work)
    clean_name = clean_security_name(security_name)
    variations = try_ticker_variations(clean_name)
    
    for ticker in variations[:3]:  # Only try first 3 variations to save time
        if test_ticker(ticker, start_date, quick_test=False):
            return ticker
        time.sleep(0.1)
    
    return None


def resolve_all_tickers(holdings_df, start_date):
    """
    Resolve tickers for all securities
    Returns: success_map, failed_list
    """
    unique_securities = holdings_df['Security Name'].unique()
    
    print(f"\n🔍 Resolving tickers for {len(unique_securities)} unique securities...")
    print("=" * 80)
    
    success_map = {}
    failed_list = []
    
    for idx, security_name in enumerate(unique_securities, 1):
        print(f"[{idx:3d}/{len(unique_securities)}] {security_name[:50]:50s} ", end='', flush=True)
        
        ticker = find_working_ticker(security_name, start_date)
        
        if ticker:
            success_map[security_name] = ticker
            print(f"✓ {ticker}")
        else:
            failed_list.append(security_name)
            print("✗ NO TICKER FOUND")
    
    print("\n" + "=" * 80)
    print(f"✅ Success: {len(success_map)}/{len(unique_securities)}")
    print(f"❌ Failed:  {len(failed_list)}/{len(unique_securities)}")
    
    return success_map, failed_list


def save_ticker_report(success_map, failed_list, output_folder='ticker_reports'):
    """Save detailed report of ticker resolution"""
    os.makedirs(output_folder, exist_ok=True)
    
    # Success report
    success_df = pd.DataFrame([
        {'Security Name': name, 'Ticker': ticker}
        for name, ticker in success_map.items()
    ])
    success_file = os.path.join(output_folder, 'successful_tickers.csv')
    success_df.to_csv(success_file, index=False)
    
    # Failed report
    failed_df = pd.DataFrame({'Security Name': failed_list})
    failed_file = os.path.join(output_folder, 'failed_tickers.csv')
    failed_df.to_csv(failed_file, index=False)
    
    # Summary report
    summary = f"""
TICKER RESOLUTION REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 80}

SUMMARY
-------
Total Securities:     {len(success_map) + len(failed_list)}
Successful:          {len(success_map)} ({len(success_map)/(len(success_map)+len(failed_list))*100:.1f}%)
Failed:              {len(failed_list)} ({len(failed_list)/(len(success_map)+len(failed_list))*100:.1f}%)

FILES GENERATED
--------------
✓ successful_tickers.csv - List of resolved tickers
✓ failed_tickers.csv     - Securities that need manual mapping

NEXT STEPS
----------
1. Review failed_tickers.csv
2. Manually add mappings to NSE_TICKER_MAP in ticker_resolver.py
3. Re-run the script

FAILED SECURITIES
-----------------
"""
    for name in failed_list[:20]:  # Show first 20
        summary += f"  - {name}\n"
    
    if len(failed_list) > 20:
        summary += f"  ... and {len(failed_list) - 20} more\n"
    
    summary_file = os.path.join(output_folder, 'ticker_resolution_summary.txt')
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"\n📄 Reports saved to: {output_folder}/")
    print(f"   - successful_tickers.csv")
    print(f"   - failed_tickers.csv")
    print(f"   - ticker_resolution_summary.txt")
    
    return success_file, failed_file, summary_file


def fetch_stock_data_batch(ticker_map, start_date, end_date=None):
    """Fetch historical data for all resolved tickers"""
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    print(f"\n📊 Fetching historical data for {len(ticker_map)} stocks...")
    print("=" * 80)
    
    stock_data = {}
    success = 0
    failed = 0
    
    for idx, (security_name, ticker) in enumerate(ticker_map.items(), 1):
        print(f"[{idx:3d}/{len(ticker_map)}] {ticker:15s} ", end='', flush=True)
        
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=end_date)
            
            if not hist.empty:
                # Remove timezone
                if hasattr(hist.index, 'tz'):
                    hist.index = hist.index.tz_localize(None)
                
                # Monthly closing prices
                monthly = hist['Close'].resample('ME').last()
                stock_data[security_name] = monthly
                print(f"✓ ({len(monthly)} months)")
                success += 1
            else:
                print("✗ (no data)")
                failed += 1
        except Exception as e:
            print(f"✗ ({str(e)[:30]})")
            failed += 1
        
        time.sleep(0.1)  # Rate limiting
    
    print("\n" + "=" * 80)
    print(f"✅ Data fetched: {success}/{len(ticker_map)}")
    print(f"❌ Failed:      {failed}/{len(ticker_map)}")
    
    return stock_data
