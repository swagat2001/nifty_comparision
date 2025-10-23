"""
NSE EQUITY MATCHER
Uses official EQUITY_L.csv from NSE to find exact ticker matches
"""
import pandas as pd
import re
from difflib import SequenceMatcher


def clean_company_name(name):
    """Clean company name for matching"""
    name = str(name).upper()
    
    # Remove common suffixes
    remove_patterns = [
        'LIMITED', 'LTD', 'LTD.', 'PRIVATE', 'PVT', 'PVT.',
        'COMPANY', 'CO', 'CO.', 'CORPORATION', 'CORP', 'CORP.',
        'ENTERPRISES', 'INDUSTRIES', 'INTERNATIONAL',
    ]
    
    for pattern in remove_patterns:
        name = re.sub(r'\b' + pattern + r'\b', '', name)
    
    # Remove equity markers and face values
    equity_patterns = [
        r'EQ\s*NEW.*', r'EQ\s*EQ', r'EQ\s*F\.?V\.?.*', r'EQ\s*RS\.?.*',
        r'NEW\s*FV.*', r'NEW\s*RS\.?.*', r'F\.?V\.?\s*RS\.?.*',
        r'RE\.?\s*\d+', r'RS\.?\s*\d+', r'\d+/-', r'\d+/\d+',
    ]
    
    for pattern in equity_patterns:
        name = re.sub(pattern, '', name, flags=re.IGNORECASE)
    
    # Remove special characters except &
    name = re.sub(r'[^\w\s&]', ' ', name)
    
    # Remove extra spaces
    name = re.sub(r'\s+', ' ', name).strip()
    
    return name


def similarity_score(str1, str2):
    """Calculate similarity between two strings"""
    return SequenceMatcher(None, str1, str2).ratio()


def load_nse_equity_list(csv_file='EQUITY_L.csv'):
    """Load official NSE equity list"""
    try:
        df = pd.read_csv(csv_file)
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Create lookup dictionary
        nse_dict = {}
        for _, row in df.iterrows():
            symbol = str(row['SYMBOL']).strip()
            company_name = str(row['NAME OF COMPANY']).strip()
            nse_dict[company_name.upper()] = symbol
        
        return nse_dict
    
    except Exception as e:
        print(f"Error loading NSE equity list: {e}")
        return {}


def find_best_match(holdings_name, nse_dict, threshold=0.8):
    """
    Find best matching ticker from NSE list
    Uses fuzzy matching for close matches
    """
    # Clean the holdings name
    clean_holdings = clean_company_name(holdings_name)
    
    # Try exact match first (cleaned)
    for nse_name, symbol in nse_dict.items():
        clean_nse = clean_company_name(nse_name)
        if clean_holdings == clean_nse:
            return symbol, 1.0, 'exact'
    
    # Try fuzzy match
    best_match = None
    best_score = 0
    best_nse_name = None
    
    for nse_name, symbol in nse_dict.items():
        clean_nse = clean_company_name(nse_name)
        score = similarity_score(clean_holdings, clean_nse)
        
        if score > best_score:
            best_score = score
            best_match = symbol
            best_nse_name = nse_name
    
    if best_score >= threshold:
        return best_match, best_score, 'fuzzy'
    
    return None, 0, 'no_match'


def match_all_holdings(holdings_df, nse_dict):
    """
    Match all holdings to NSE tickers
    Returns: matched_dict, unmatched_list
    """
    print("\n" + "="*80)
    print("MATCHING HOLDINGS TO NSE EQUITY LIST")
    print("="*80)
    print(f"\nNSE Equity List: {len(nse_dict)} companies")
    print(f"Holdings to match: {len(holdings_df['Security Name'].unique())}")
    print("\n" + "="*80 + "\n")
    
    matched = {}
    unmatched = []
    
    unique_securities = holdings_df['Security Name'].unique()
    
    for idx, security_name in enumerate(unique_securities, 1):
        print(f"[{idx:3d}/{len(unique_securities)}] {security_name[:50]:50s} ", end='', flush=True)
        
        ticker, score, match_type = find_best_match(security_name, nse_dict)
        
        if ticker:
            matched[security_name] = ticker
            if match_type == 'exact':
                print(f"✓ {ticker:15s} (exact)")
            else:
                print(f"≈ {ticker:15s} (fuzzy {score:.0%})")
        else:
            unmatched.append(security_name)
            print("✗ no match")
    
    print("\n" + "="*80)
    print("MATCHING COMPLETE")
    print("="*80)
    print(f"✓ Matched:   {len(matched)}/{len(unique_securities)} ({len(matched)/len(unique_securities)*100:.1f}%)")
    print(f"✗ Unmatched: {len(unmatched)}/{len(unique_securities)}")
    print("="*80 + "\n")
    
    return matched, unmatched


def save_matched_tickers(matched_dict, output_file='nse_matched_tickers.csv'):
    """Save matched tickers to CSV"""
    df = pd.DataFrame([
        {'Security_Name': name, 'NSE_Symbol': ticker}
        for name, ticker in matched_dict.items()
    ])
    
    df.to_csv(output_file, index=False)
    print(f"✓ Saved matched tickers to: {output_file}")


def generate_validated_tickers_code(matched_dict, output_file='nse_mappings_to_add.py'):
    """Generate Python code to add to validated_tickers.py"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# NSE EQUITY LIST MAPPINGS\n")
        f.write("# Add these to VALIDATED_NSE_TICKERS in validated_tickers.py\n\n")
        f.write("NSE_MAPPINGS = {\n")
        
        for security, ticker in sorted(matched_dict.items()):
            f.write(f"    '{security}': '{ticker}',\n")
        
        f.write("}\n")
    
    print(f"✓ Saved Python mappings to: {output_file}")


def update_validated_tickers(matched_dict):
    """Directly update validated_tickers.py with NSE matches"""
    import shutil
    
    print("\nUpdating validated_tickers.py...")
    
    # Backup
    backup_file = 'validated_tickers_BACKUP.py'
    try:
        shutil.copy('validated_tickers.py', backup_file)
        print(f"✓ Backup created: {backup_file}")
    except:
        print("⚠️  Could not create backup")
    
    # Read existing
    try:
        with open('validated_tickers.py', 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        print("❌ Could not read validated_tickers.py")
        return False
    
    # Find dictionary end
    dict_end = content.rfind('}')
    if dict_end == -1:
        print("❌ Could not find dictionary")
        return False
    
    # Generate entries
    new_entries = "\n    # === NSE EQUITY LIST MATCHES ===\n"
    for security, ticker in sorted(matched_dict.items()):
        new_entries += f"    '{security}': '{ticker}',\n"
    
    # Update
    updated_content = content[:dict_end] + new_entries + content[dict_end:]
    
    with open('validated_tickers.py', 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"✓ Updated validated_tickers.py with {len(matched_dict)} mappings")
    
    return True


def main():
    """Main matching workflow"""
    
    # Load NSE equity list
    print("Loading NSE EQUITY_L.csv...")
    nse_dict = load_nse_equity_list('EQUITY_L.csv')
    
    if not nse_dict:
        print("❌ Could not load NSE equity list")
        print("Please ensure EQUITY_L.csv is in the current directory")
        return
    
    print(f"✓ Loaded {len(nse_dict)} NSE companies\n")
    
    # Load holdings
    print("Loading holdings...")
    try:
        from data_loader import load_holdings_data
        holdings_df = load_holdings_data()
        print(f"✓ Loaded {len(holdings_df)} holdings\n")
    except:
        print("❌ Could not load holdings")
        return
    
    # Match holdings to NSE tickers
    matched, unmatched = match_all_holdings(holdings_df, nse_dict)
    
    # Save results
    save_matched_tickers(matched, 'nse_matched_tickers.csv')
    generate_validated_tickers_code(matched, 'nse_mappings_to_add.py')
    
    # Update validated_tickers.py
    if matched:
        update_validated_tickers(matched)
    
    # Save unmatched
    if unmatched:
        unmatched_df = pd.DataFrame({'Security_Name': unmatched})
        unmatched_df.to_csv('nse_unmatched.csv', index=False)
        print(f"✓ Saved unmatched securities to: nse_unmatched.csv")
    
    print("\n" + "="*80)
    print("✅ NSE MATCHING COMPLETE!")
    print("="*80)
    print(f"\nTotal matched: {len(matched)} securities")
    print(f"Coverage: {len(matched)/(len(matched)+len(unmatched))*100:.1f}%")
    print("\nFiles created:")
    print("  - nse_matched_tickers.csv (all matches)")
    print("  - nse_mappings_to_add.py (Python code)")
    print("  - nse_unmatched.csv (securities still missing)")
    print("\nvalidated_tickers.py has been updated!")
    print("\nRun: python main.py")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()