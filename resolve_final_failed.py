"""
FINAL FAILED TICKERS RESOLVER
Uses NSE EQUITY_L.csv to resolve remaining failed tickers
Advanced fuzzy matching with manual overrides
"""
import pandas as pd
import re
from difflib import SequenceMatcher


# Manual overrides for tricky matches
MANUAL_OVERRIDES = {
    'CREDO BRANDS MARKETING LIMITED': 'CREDOBRAND',
    'KSR FOOTWEAR LIMITED': 'KSR',
    'THAMBBI MODERN SPINNING MILLS LIMITED': 'THAMBIMIL',
    'ACTION CONSTRUCTION EQUIPMENT LIMITED': 'ACE',
    'ANIL BIOPLUS LIMITED': 'ANILBIO',
    'ANIL LIMITED': 'ANILLTD',
    'PAE LIMITED': 'PAE',
    'STERLITE ELECTRIC LIMITED': 'STRTECH',
    'STERLITE GRID 5 LIMITED': 'STRTECH',  # Same as Sterlite Technologies
    'STERLITE TECHNOLOGIES LIMITED': 'STRTECH',
    'STL NETWORKS LIMITED': 'STLNETWORK',
    'GUJARAT NRE COKE LIMITED': 'GUJNRECOKE',
    'L&T FINANCE LIMITED': 'L&TFH',
    'LML LIMITED': 'LML',
    'M.G.F. GROWTH RESEARCH AND INVESMART LIMITED': 'MGFGRO',
    'DILIGENT MEDIA CORPORATION LIMITED': 'DILIGENT',
    'AADHAR HOUSING FINANCE LIMITED': 'AADHARHFC',
    'AUTOMOBILE CORPORATION OF GOA LIMITED': 'AUTOCORPGOA',
    'AVANCE TECHNOLOGIES LIMITED': 'AVANCE',
    'ELGI EQUIPMENTS LIMITED': 'ELGIEQUIP',
    'EMCURE PHARMACEUTICALS LIMITED': 'EMCURE',
    'GODREJ AGROVET LIMITED': 'GODREJAGRV',
    'INDIA PESTICIDES LIMITED': 'INDIAPESTC',
    'KAASHYAP TECHNOLOGIES LIMITED': 'KAASHYAP',
    'KALPATARU PROJECTS INTERNATIONAL LIMITED': 'KALPATARU',
    'SANSTAR LIMITED': 'SANSTAR',
    'SARASWATI SAREE DEPOT LIMITED': 'SARASWATI',
    'SHRI LAKSHMI COTSYN LIMITED': 'SLCL',
    'TML COMMERCIAL VEHICLES LIMITED': 'TMLBSNL',
    'VIKRAM SOLAR LIMITED': 'VIKRAMSOLR',
    'W S INDUSTRIES (INDIA) LIMITED': 'WSINDIA',
    'ZENITH HEALTHCARE LIMITED': 'ZENITHHEALTH',
    'ASHIMA LIMITED': 'ASHIMASYN',
    'NOVA STEELS (INDIA) LIMITED': 'NOVASTEEL',
    'SUPREME PETROCHEM LIMITED': 'SUPPETRO',
    'MODERN INSULATORS LIMITED': 'MODIINSUL',
    'WINDSOR MACHINES LIMITED': 'WINDMACHIN',
    'BIRLASOFT LIMITED': 'BSOFT',
    'CENTRAL BANK OF INDIA': 'CENTRALBK',
    'CITY UNION BANK LIMITED': 'CUB',
    'ENGINEERS INDIA LIMITED': 'ENGINERSIN',
    'INDO COUNT INDUSTRIES LIMITED': 'ICIL',
    'SHREE RENUKA SUGARS LIMITED': 'RENUKA',
}


def aggressive_clean(name):
    """Aggressive cleaning for matching"""
    name = str(name).upper()
    
    # Remove everything after certain keywords
    for stop in ['PREF', 'BD ', 'BOND', 'ETF', 'MUTUAL FUND']:
        if stop in name:
            name = name.split(stop)[0]
    
    # Remove all non-alphabetic except spaces and &
    name = re.sub(r'[^A-Z\s&]', '', name)
    
    # Remove common words
    remove = ['LIMITED', 'LTD', 'COMPANY', 'CORPORATION', 'INDUSTRIES',
              'INDIA', 'INTERNATIONAL', 'PRIVATE', 'PUBLIC', 'ENTERPRISES']
    
    for word in remove:
        name = re.sub(r'\b' + word + r'\b', '', name)
    
    # Clean spaces
    name = re.sub(r'\s+', ' ', name).strip()
    
    return name


def similarity_ratio(s1, s2):
    """Calculate similarity between strings"""
    return SequenceMatcher(None, s1.upper(), s2.upper()).ratio()


def find_best_nse_match(security_name, nse_df, threshold=0.75):
    """Find best match in NSE list"""
    
    # Check manual overrides first
    clean_name = aggressive_clean(security_name)
    
    for key, ticker in MANUAL_OVERRIDES.items():
        if aggressive_clean(key) == clean_name:
            return ticker, 1.0, 'manual'
    
    # Try exact symbol match
    clean_parts = clean_name.split()
    if len(clean_parts) > 0:
        first_word = clean_parts[0]
        
        # Check if first word is a ticker
        match = nse_df[nse_df['SYMBOL'].str.upper() == first_word]
        if len(match) > 0:
            return match.iloc[0]['SYMBOL'], 0.95, 'symbol'
    
    # Fuzzy match on company name
    best_match = None
    best_score = 0
    
    for _, row in nse_df.iterrows():
        nse_name = aggressive_clean(row['NAME OF COMPANY'])
        score = similarity_ratio(clean_name, nse_name)
        
        if score > best_score:
            best_score = score
            best_match = row['SYMBOL']
    
    if best_score >= threshold:
        return best_match, best_score, 'fuzzy'
    
    return None, 0, 'failed'


def resolve_failed_tickers(failed_csv, equity_csv='EQUITY_L.csv'):
    """Resolve all failed tickers"""
    
    print("\n" + "="*80)
    print("RESOLVING FAILED TICKERS")
    print("="*80 + "\n")
    
    # Load files
    try:
        failed_df = pd.read_csv(failed_csv)
        nse_df = pd.read_csv(equity_csv)
        nse_df.columns = nse_df.columns.str.strip()
    except Exception as e:
        print(f"❌ Error loading files: {e}")
        return
    
    print(f"Failed tickers to resolve: {len(failed_df)}")
    print(f"NSE companies available: {len(nse_df)}")
    print("\n" + "="*80 + "\n")
    
    # Resolve each
    resolved = {}
    still_failed = []
    
    for idx, row in failed_df.iterrows():
        security = row['Security Name']
        
        # Skip if it's a bond/preference share
        if any(x in str(security).upper() for x in ['BD ', 'PREF', 'BOND', 'ETF']):
            still_failed.append(security)
            continue
        
        print(f"[{idx+1:3d}/{len(failed_df)}] {security[:55]:55s} ", end='', flush=True)
        
        ticker, score, method = find_best_nse_match(security, nse_df)
        
        if ticker:
            resolved[security] = ticker
            
            if method == 'manual':
                print(f"✓ {ticker:15s} (manual)")
            elif method == 'symbol':
                print(f"✓ {ticker:15s} (symbol)")
            else:
                print(f"≈ {ticker:15s} (fuzzy {score:.0%})")
        else:
            still_failed.append(security)
            print("✗")
    
    print("\n" + "="*80)
    print("RESOLUTION COMPLETE")
    print("="*80)
    print(f"✓ Resolved: {len(resolved)}/{len(failed_df)} ({len(resolved)/len(failed_df)*100:.1f}%)")
    print(f"✗ Still failed: {len(still_failed)}")
    print("="*80 + "\n")
    
    return resolved, still_failed


def update_validated_tickers_with_resolved(resolved_dict):
    """Add resolved tickers to validated_tickers.py"""
    import shutil
    
    if not resolved_dict:
        print("No tickers to add")
        return
    
    print("Updating validated_tickers.py...")
    
    # Backup
    try:
        shutil.copy('validated_tickers.py', 'validated_tickers_BACKUP.py')
        print(f"✓ Backup created")
    except:
        pass
    
    # Read
    try:
        with open('validated_tickers.py', 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        print("❌ Could not read file")
        return
    
    # Find end
    dict_end = content.rfind('}')
    if dict_end == -1:
        print("❌ Could not find dictionary")
        return
    
    # Generate entries
    new_entries = "\n    # === RESOLVED FAILED TICKERS ===\n"
    for security, ticker in sorted(resolved_dict.items()):
        # Escape apostrophes
        security_escaped = security.replace("'", "\\'")
        new_entries += f"    '{security_escaped}': '{ticker}',\n"
    
    # Update
    updated_content = content[:dict_end] + new_entries + content[dict_end:]
    
    with open('validated_tickers.py', 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"✓ Added {len(resolved_dict)} resolved tickers")


def save_reports(resolved, still_failed):
    """Save resolution reports"""
    
    # Resolved tickers
    if resolved:
        resolved_df = pd.DataFrame([
            {'Security_Name': name, 'NSE_Ticker': ticker}
            for name, ticker in resolved.items()
        ])
        resolved_df.to_csv('ticker_reports/resolved_tickers.csv', index=False)
        print(f"✓ Saved: ticker_reports/resolved_tickers.csv")
    
    # Still failed
    if still_failed:
        failed_df = pd.DataFrame({'Security_Name': still_failed})
        failed_df.to_csv('ticker_reports/still_failed_tickers.csv', index=False)
        print(f"✓ Saved: ticker_reports/still_failed_tickers.csv")


def main():
    """Main resolution workflow"""
    
    failed_csv = 'ticker_reports/failed_tickers.csv'
    
    # Check if files exist
    import os
    if not os.path.exists(failed_csv):
        print(f"❌ Could not find {failed_csv}")
        return
    
    if not os.path.exists('EQUITY_L.csv'):
        print("❌ Could not find EQUITY_L.csv")
        print("Please ensure EQUITY_L.csv is in the current directory")
        return
    
    # Resolve tickers
    resolved, still_failed = resolve_failed_tickers(failed_csv, 'EQUITY_L.csv')
    
    # Save reports
    save_reports(resolved, still_failed)
    
    # Update validated_tickers.py
    if resolved:
        update_validated_tickers_with_resolved(resolved)
    
    print("\n" + "="*80)
    print("✅ RESOLUTION COMPLETE!")
    print("="*80)
    print(f"\nResolved {len(resolved)} additional tickers")
    print(f"Remaining failed: {len(still_failed)}")
    
    if len(still_failed) > 0:
        print("\nStill failed securities are mostly:")
        print("  - Bonds/Debentures")
        print("  - ETFs/Mutual Funds")
        print("  - Delisted companies")
        print("  - Preference shares")
        print("\nThese can be safely ignored for equity analysis")
    
    print("\nvalidated_tickers.py has been updated!")
    print("\nRun: python main.py")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()