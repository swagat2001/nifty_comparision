"""
Configuration for Investment Comparison Analysis
Auto-detected Excel files and sheet names
"""
import os
from pathlib import Path

# Get the directory where this script is located
PROJECT_DIR = Path(__file__).parent.absolute()

# Data files - auto-detected
HOLDINGS_FILE = PROJECT_DIR / 'Demat Holding_Nil_Trade_01.07.2025.xlsx'
HOLDINGS_SHEET = 'DETAILED_HOLDING'

WEIGHTS_FILE = PROJECT_DIR / 'CURRENT_WEIGHATGE_(Aug 25).xlsx'
MULTI_CAP_SHEET = 'Sheet'
MID_SMALL_CAP_SHEET = 'Sheet'

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
NIFTY_INDICES = {
    "NIFTY 50": "^NSEI",
}

# Debug info
if __name__ == "__main__":
    print("\n" + "="*80)
    print("CONFIGURATION CHECK")
    print("="*80)
    print(f"\nProject Directory: {PROJECT_DIR}")
    print(f"\nData Files:")
    print(f"  Holdings: {HOLDINGS_FILE}")
    print(f"    Sheet:  'DETAILED_HOLDING'")
    print(f"    Exists: {HOLDINGS_FILE.exists()}")
    print(f"  Weights:  {WEIGHTS_FILE}")
    print(f"    Multi Cap Sheet: 'Sheet'")
    print(f"    Mid/Small Sheet: 'Sheet'")
    print(f"    Exists: {WEIGHTS_FILE.exists()}")
    print(f"\nDirectories:")
    print(f"  Data:    {DATA_DIR}")
    print(f"  Output:  {OUTPUT_DIR}")
    print(f"  Reports: {REPORTS_DIR}")
    print("="*80 + "\n")
