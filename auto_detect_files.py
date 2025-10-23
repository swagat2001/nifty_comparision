"""
AUTO-DETECT EXCEL FILES
Finds and configures correct Excel filenames
"""
import os
from pathlib import Path


def find_excel_files():
    """Find all Excel files in current directory"""
    project_dir = Path.cwd()
    excel_files = list(project_dir.glob('*.xlsx'))
    
    print("\n" + "="*80)
    print("EXCEL FILES FOUND")
    print("="*80 + "\n")
    
    holdings_files = []
    weights_files = []
    
    for file in excel_files:
        print(f"  {file.name}")
        
        # Categorize files
        name_lower = file.name.lower()
        if 'demat' in name_lower or 'holding' in name_lower or 'nil' in name_lower or 'nii' in name_lower:
            holdings_files.append(file)
        elif 'weight' in name_lower or 'current' in name_lower:
            weights_files.append(file)
    
    print("\n" + "="*80)
    print("CATEGORIZED FILES")
    print("="*80)
    print(f"\n📊 Holdings Files ({len(holdings_files)}):")
    for f in holdings_files:
        print(f"  - {f.name}")
    
    print(f"\n📈 Weights Files ({len(weights_files)}):")
    for f in weights_files:
        print(f"  - {f.name}")
    
    return holdings_files, weights_files


def update_config_with_correct_files(holdings_file, weights_file):
    """Update config.py with correct filenames"""
    
    config_content = f'''"""
Configuration for Investment Comparison Analysis
Auto-detected Excel file paths
"""
import os
from pathlib import Path

# Get the directory where this script is located
PROJECT_DIR = Path(__file__).parent.absolute()

# Data files - auto-detected
HOLDINGS_FILE = PROJECT_DIR / '{holdings_file.name}'
HOLDINGS_SHEET = 'Demat Holding Report'

WEIGHTS_FILE = PROJECT_DIR / '{weights_file.name}'
MULTI_CAP_SHEET = 'GM Multi Cap Fund'
MID_SMALL_CAP_SHEET = 'GM Mid & Small Cap Fund'

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
    print(f"    Exists: {{HOLDINGS_FILE.exists()}}")
    print(f"  Weights:  {{WEIGHTS_FILE}}")
    print(f"    Exists: {{WEIGHTS_FILE.exists()}}")
    print(f"\\nDirectories:")
    print(f"  Data:    {{DATA_DIR}}")
    print(f"  Output:  {{OUTPUT_DIR}}")
    print(f"  Reports: {{REPORTS_DIR}}")
    print("="*80 + "\\n")
'''
    
    with open('config.py', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("\n✓ Updated config.py with correct filenames")


def main():
    """Main workflow"""
    print("\n" + "="*80)
    print("AUTO-DETECTING EXCEL FILES")
    print("="*80)
    
    holdings_files, weights_files = find_excel_files()
    
    if not holdings_files:
        print("\n❌ No holdings file found!")
        print("Please ensure you have a file with 'Demat' or 'Holding' in the name")
        return
    
    if not weights_files:
        print("\n❌ No weights file found!")
        print("Please ensure you have a file with 'Weight' or 'Current' in the name")
        return
    
    # Use first match
    holdings_file = holdings_files[0]
    weights_file = weights_files[0]
    
    print("\n" + "="*80)
    print("SELECTED FILES")
    print("="*80)
    print(f"\n✓ Holdings: {holdings_file.name}")
    print(f"✓ Weights:  {weights_file.name}")
    
    # Update config
    update_config_with_correct_files(holdings_file, weights_file)
    
    print("\n" + "="*80)
    print("✅ CONFIGURATION UPDATED!")
    print("="*80)
    print("\nYou can now run: python main.py")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()