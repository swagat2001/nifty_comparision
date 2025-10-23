"""
SHEET NAME DETECTOR
Finds correct sheet names in Excel files
"""
import pandas as pd
from pathlib import Path


def detect_sheet_names(excel_file):
    """Detect all sheet names in an Excel file"""
    try:
        xl_file = pd.ExcelFile(excel_file)
        return xl_file.sheet_names
    except Exception as e:
        print(f"Error reading {excel_file.name}: {e}")
        return []


def preview_sheet_data(excel_file, sheet_name, rows=5):
    """Preview first few rows of a sheet"""
    try:
        df = pd.read_excel(excel_file, sheet_name=sheet_name, nrows=rows)
        return df
    except Exception as e:
        return None


def find_holdings_sheet(excel_file):
    """Find the most likely holdings sheet"""
    sheets = detect_sheet_names(excel_file)
    
    print(f"\n📊 {excel_file.name}")
    print("="*80)
    print(f"Found {len(sheets)} sheets:\n")
    
    for idx, sheet in enumerate(sheets, 1):
        print(f"  {idx}. {sheet}")
        
        # Preview data
        df = preview_sheet_data(excel_file, sheet, rows=3)
        if df is not None and len(df) > 0:
            print(f"     Columns: {', '.join(df.columns[:5].tolist())}")
            if len(df.columns) > 5:
                print(f"              ... and {len(df.columns) - 5} more")
        print()
    
    return sheets


def find_fund_sheets(excel_file):
    """Find fund weight sheets"""
    sheets = detect_sheet_names(excel_file)
    
    print(f"\n📈 {excel_file.name}")
    print("="*80)
    print(f"Found {len(sheets)} sheets:\n")
    
    multi_cap_sheet = None
    mid_small_sheet = None
    
    for idx, sheet in enumerate(sheets, 1):
        print(f"  {idx}. {sheet}")
        
        # Check if it's a fund sheet
        sheet_lower = sheet.lower()
        if 'multi' in sheet_lower and 'cap' in sheet_lower:
            multi_cap_sheet = sheet
            print(f"     ✓ Detected as Multi Cap Fund sheet")
        elif 'mid' in sheet_lower and 'small' in sheet_lower:
            mid_small_sheet = sheet
            print(f"     ✓ Detected as Mid & Small Cap Fund sheet")
        
        # Preview data
        df = preview_sheet_data(excel_file, sheet, rows=3)
        if df is not None and len(df) > 0:
            print(f"     Columns: {', '.join(df.columns[:5].tolist())}")
            if len(df.columns) > 5:
                print(f"              ... and {len(df.columns) - 5} more")
        print()
    
    return sheets, multi_cap_sheet, mid_small_sheet


def update_config_with_sheets(holdings_file, holdings_sheet, weights_file, 
                               multi_cap_sheet, mid_small_sheet):
    """Update config.py with correct sheet names"""
    
    config_content = f'''"""
Configuration for Investment Comparison Analysis
Auto-detected Excel files and sheet names
"""
import os
from pathlib import Path

# Get the directory where this script is located
PROJECT_DIR = Path(__file__).parent.absolute()

# Data files - auto-detected
HOLDINGS_FILE = PROJECT_DIR / '{holdings_file.name}'
HOLDINGS_SHEET = '{holdings_sheet}'

WEIGHTS_FILE = PROJECT_DIR / '{weights_file.name}'
MULTI_CAP_SHEET = '{multi_cap_sheet}'
MID_SMALL_CAP_SHEET = '{mid_small_sheet}'

# Investment start date
INVESTMENT_DATE = '2024-04-01'

# Directory structure
DATA_DIR = PROJECT_DIR / 'data'
OUTPUT_DIR = PROJECT_DIR / 'output'
REPORTS_DIR = PROJECT_DIR / 'reports'

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# NIFTY indices to compare (only NIFTY 50)
NIFTY_INDICES = {{
    "NIFTY 50": "^NSEI",
}}

# Debug info
if __name__ == "__main__":
    print("\\n" + "="*80)
    print("CONFIGURATION CHECK")
    print("="*80)
    print(f"\\nProject Directory: {{PROJECT_DIR}}")
    print(f"\\nData Files:")
    print(f"  Holdings: {{HOLDINGS_FILE}}")
    print(f"    Sheet:  '{holdings_sheet}'")
    print(f"    Exists: {{HOLDINGS_FILE.exists()}}")
    print(f"  Weights:  {{WEIGHTS_FILE}}")
    print(f"    Multi Cap Sheet: '{multi_cap_sheet}'")
    print(f"    Mid/Small Sheet: '{mid_small_sheet}'")
    print(f"    Exists: {{WEIGHTS_FILE.exists()}}")
    print(f"\\nDirectories:")
    print(f"  Data:    {{DATA_DIR}}")
    print(f"  Output:  {{OUTPUT_DIR}}")
    print(f"  Reports: {{REPORTS_DIR}}")
    print("="*80 + "\\n")
'''
    
    with open('config.py', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("\n✓ Updated config.py")


def main():
    """Main workflow"""
    print("\n" + "="*80)
    print("EXCEL SHEET NAME DETECTOR")
    print("="*80)
    
    # Find Excel files
    excel_files = list(Path.cwd().glob('*.xlsx'))
    
    if not excel_files:
        print("\n❌ No Excel files found!")
        return
    
    holdings_files = []
    weights_files = []
    
    for file in excel_files:
        name_lower = file.name.lower()
        if 'demat' in name_lower or 'holding' in name_lower or 'nil' in name_lower:
            holdings_files.append(file)
        elif 'weight' in name_lower or 'current' in name_lower:
            weights_files.append(file)
    
    if not holdings_files or not weights_files:
        print("\n❌ Could not find both holdings and weights files!")
        print("Holdings files:", [f.name for f in holdings_files])
        print("Weights files:", [f.name for f in weights_files])
        return
    
    holdings_file = holdings_files[0]
    weights_file = weights_files[0]
    
    # Detect sheet names
    print("\n" + "="*80)
    print("DETECTING SHEET NAMES")
    print("="*80)
    
    # Holdings sheets
    holdings_sheets = find_holdings_sheet(holdings_file)
    
    if not holdings_sheets:
        print("\n❌ No sheets found in holdings file!")
        return
    
    # Ask user to select holdings sheet
    print("\n" + "="*80)
    print("SELECT HOLDINGS SHEET")
    print("="*80)
    print(f"\nWhich sheet contains the holdings data?")
    for idx, sheet in enumerate(holdings_sheets, 1):
        print(f"  {idx}. {sheet}")
    
    while True:
        try:
            choice = int(input(f"\nEnter number (1-{len(holdings_sheets)}): "))
            if 1 <= choice <= len(holdings_sheets):
                holdings_sheet = holdings_sheets[choice - 1]
                break
            else:
                print(f"Please enter a number between 1 and {len(holdings_sheets)}")
        except ValueError:
            print("Please enter a valid number")
    
    # Fund sheets
    fund_sheets, auto_multi_cap, auto_mid_small = find_fund_sheets(weights_file)
    
    if not fund_sheets:
        print("\n❌ No sheets found in weights file!")
        return
    
    # Select Multi Cap sheet
    print("\n" + "="*80)
    print("SELECT MULTI CAP FUND SHEET")
    print("="*80)
    if auto_multi_cap:
        print(f"\nAuto-detected: {auto_multi_cap}")
        use_auto = input("Use this sheet? (yes/no): ").strip().lower()
        if use_auto in ['yes', 'y']:
            multi_cap_sheet = auto_multi_cap
        else:
            multi_cap_sheet = None
    else:
        multi_cap_sheet = None
    
    if not multi_cap_sheet:
        print(f"\nWhich sheet contains GM Multi Cap Fund data?")
        for idx, sheet in enumerate(fund_sheets, 1):
            print(f"  {idx}. {sheet}")
        
        while True:
            try:
                choice = int(input(f"\nEnter number (1-{len(fund_sheets)}): "))
                if 1 <= choice <= len(fund_sheets):
                    multi_cap_sheet = fund_sheets[choice - 1]
                    break
            except ValueError:
                pass
    
    # Select Mid & Small Cap sheet
    print("\n" + "="*80)
    print("SELECT MID & SMALL CAP FUND SHEET")
    print("="*80)
    if auto_mid_small:
        print(f"\nAuto-detected: {auto_mid_small}")
        use_auto = input("Use this sheet? (yes/no): ").strip().lower()
        if use_auto in ['yes', 'y']:
            mid_small_sheet = auto_mid_small
        else:
            mid_small_sheet = None
    else:
        mid_small_sheet = None
    
    if not mid_small_sheet:
        print(f"\nWhich sheet contains GM Mid & Small Cap Fund data?")
        for idx, sheet in enumerate(fund_sheets, 1):
            print(f"  {idx}. {sheet}")
        
        while True:
            try:
                choice = int(input(f"\nEnter number (1-{len(fund_sheets)}): "))
                if 1 <= choice <= len(fund_sheets):
                    mid_small_sheet = fund_sheets[choice - 1]
                    break
            except ValueError:
                pass
    
    # Update config
    print("\n" + "="*80)
    print("SELECTED CONFIGURATION")
    print("="*80)
    print(f"\n✓ Holdings File: {holdings_file.name}")
    print(f"  Sheet: '{holdings_sheet}'")
    print(f"\n✓ Weights File: {weights_file.name}")
    print(f"  Multi Cap Sheet: '{multi_cap_sheet}'")
    print(f"  Mid/Small Sheet: '{mid_small_sheet}'")
    
    update_config_with_sheets(
        holdings_file, holdings_sheet,
        weights_file, multi_cap_sheet, mid_small_sheet
    )
    
    print("\n" + "="*80)
    print("✅ CONFIGURATION UPDATED!")
    print("="*80)
    print("\nYou can now run: python main.py")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()