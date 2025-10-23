"""
QUICK FIX - Detect and update fund sheet names
"""
import pandas as pd
from pathlib import Path

# Your weights file
WEIGHTS_FILE = Path(r"C:\Users\swaga\OneDrive\Desktop\nifty_comparision\CURRENT_WEIGHATGE_(Aug 25).xlsx")

print("\n" + "="*80)
print("QUICK FIX - DETECTING FUND SHEETS")
print("="*80)

# Load Excel and show all sheets
xl = pd.ExcelFile(WEIGHTS_FILE)
print(f"\nFound {len(xl.sheet_names)} sheets:")
for i, sheet in enumerate(xl.sheet_names, 1):
    print(f"  {i}. {sheet}")

# Let user select
print("\n" + "="*80)
print("SELECT SHEETS")
print("="*80)

print("\nWhich sheet is GM Multi Cap Fund?")
multi_cap_choice = int(input(f"Enter number (1-{len(xl.sheet_names)}): ")) - 1
multi_cap_sheet = xl.sheet_names[multi_cap_choice]

print("\nWhich sheet is GM Mid & Small Cap Fund?")
mid_small_choice = int(input(f"Enter number (1-{len(xl.sheet_names)}): ")) - 1
mid_small_sheet = xl.sheet_names[mid_small_choice]

# Update config.py
config_content = f'''"""
Configuration for Investment Comparison Analysis
"""
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.absolute()

# Data files
HOLDINGS_FILE = PROJECT_DIR / 'Demat Holding_NII_Trade_01.07.2025.xlsx'
HOLDINGS_SHEET = 'DETAILED_HOLDING'

WEIGHTS_FILE = PROJECT_DIR / 'CURRENT_WEIGHATGE_(Aug 25).xlsx'
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

# NIFTY indices to compare
NIFTY_INDICES = {{
    "NIFTY 50": "^NSEI",
}}
'''

with open('config.py', 'w', encoding='utf-8') as f:
    f.write(config_content)

print("\n" + "="*80)
print("✅ CONFIGURATION UPDATED!")
print("="*80)
print(f"\nMulti Cap Sheet: '{multi_cap_sheet}'")
print(f"Mid & Small Cap Sheet: '{mid_small_sheet}'")
print("\nNow run: python main.py")
print("="*80 + "\n")