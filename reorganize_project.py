"""
PROJECT REORGANIZATION SCRIPT
Cleans up and organizes the project into proper directories
"""
import os
import shutil
from pathlib import Path


# Project structure
PROJECT_STRUCTURE = {
    'data': 'All scraped stock data',
    'output': 'Generated charts and reports',
    'reports': 'Ticker reports and analysis',
}

# Core files to keep
CORE_FILES = [
    'main.py',
    'config.py',
    'data_loader.py',
    'data_scraper.py',
    'ticker_resolver.py',
    'validated_tickers.py',
    'smart_calculator.py',
    'visualizer.py',
    'market_data.py',
    'requirements.txt',
]

# Utility files (optional)
UTILITY_FILES = [
    'nse_equity_matcher.py',
    'fix_syntax_errors.py',
]

# Files to DELETE
DELETE_FILES = [
    'add_all_verified_mappings.py',
    'add_manual_mappings.py',
    'add_ultimate_mappings.py',
    'auto_update_tickers.py',
    'cleanup_project.py',
    'merge_yahoo_tickers.py',
    'nse_mappings_to_add.py',
    'resolve_final_failed.py',
    'Validate_yahoo_tickers___PY',
    'validated_tickers_BACKUP.py',
    'validated_tickers_UPDATED.py',
    'validate_yahoo_tickers.py',
    'manual_mapper.py',
    'stock_scraper.py',
    'nifty_data.py',
    'calculator.py',
    'portfolio_calculator.py',
    'visualization.py',
]


def create_directory_structure():
    """Create organized directory structure"""
    print("\n" + "="*80)
    print("CREATING DIRECTORY STRUCTURE")
    print("="*80 + "\n")
    
    for dir_name, description in PROJECT_STRUCTURE.items():
        os.makedirs(dir_name, exist_ok=True)
        print(f"✓ Created: {dir_name}/ - {description}")
    
    print()


def move_existing_data():
    """Move existing data to proper directories"""
    print("\n" + "="*80)
    print("ORGANIZING EXISTING DATA")
    print("="*80 + "\n")
    
    # Move scraped_data to data directory
    if os.path.exists('scraped_data'):
        if os.path.exists('data/scraped_data'):
            shutil.rmtree('data/scraped_data')
        shutil.move('scraped_data', 'data/scraped_data')
        print("✓ Moved: scraped_data/ → data/scraped_data/")
    
    # Move ticker_reports to reports directory
    if os.path.exists('ticker_reports'):
        if os.path.exists('reports/ticker_reports'):
            shutil.rmtree('reports/ticker_reports')
        shutil.move('ticker_reports', 'reports/ticker_reports')
        print("✓ Moved: ticker_reports/ → reports/ticker_reports/")
    
    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)
    
    print()


def delete_obsolete_files():
    """Delete unnecessary files"""
    print("\n" + "="*80)
    print("REMOVING OBSOLETE FILES")
    print("="*80 + "\n")
    
    deleted_count = 0
    
    for filename in DELETE_FILES:
        if os.path.exists(filename):
            try:
                os.remove(filename)
                print(f"✓ Deleted: {filename}")
                deleted_count += 1
            except Exception as e:
                print(f"✗ Could not delete {filename}: {e}")
    
    print(f"\n✓ Deleted {deleted_count} obsolete files\n")


def show_final_structure():
    """Display final project structure"""
    print("\n" + "="*80)
    print("FINAL PROJECT STRUCTURE")
    print("="*80 + "\n")
    
    structure = """
nifty_comparision/
│
├── 📁 data/                          # All data storage
│   └── scraped_data/                 # Downloaded stock prices
│       ├── prices/                   # Individual stock CSVs
│       └── download_state.json       # Download tracking
│
├── 📁 output/                        # Generated visualizations
│   └── investment_comparison_*.html  # Interactive charts
│
├── 📁 reports/                       # Analysis reports
│   └── ticker_reports/               # Ticker resolution reports
│       ├── successful_tickers.csv
│       ├── failed_tickers.csv
│       └── coverage_report.csv
│
├── 📄 main.py                        # Main analysis script
├── 📄 config.py                      # Configuration
├── 📄 data_loader.py                 # Load Excel data
├── 📄 data_scraper.py                # Download stock prices
├── 📄 ticker_resolver.py             # Resolve tickers
├── 📄 validated_tickers.py           # Ticker database
├── 📄 smart_calculator.py            # Portfolio calculations
├── 📄 visualizer.py                  # Create charts
├── 📄 market_data.py                 # NIFTY data
│
├── 📄 nse_equity_matcher.py          # (Utility) NSE matcher
├── 📄 fix_syntax_errors.py           # (Utility) Fix syntax
│
├── 📄 requirements.txt               # Dependencies
├── 📄 EQUITY_L.csv                   # NSE equity list
└── 📄 [Excel data files]             # Holdings data
    """
    
    print(structure)
    
    print("="*80)
    print("✅ PROJECT REORGANIZED!")
    print("="*80)
    print("\nKey improvements:")
    print("  ✓ Clean directory structure")
    print("  ✓ Data isolated in data/ folder")
    print("  ✓ Charts isolated in output/ folder")
    print("  ✓ Reports isolated in reports/ folder")
    print("  ✓ Removed 15+ obsolete files")
    print("  ✓ Only 9 core Python files in root")
    print("\nNext steps:")
    print("  1. Run: python main.py")
    print("  2. Data will be cached in data/scraped_data/")
    print("  3. Charts will be saved in output/")
    print("  4. Reports will be saved in reports/")
    print("="*80 + "\n")


def update_config_paths():
    """Update config.py with new directory paths"""
    print("\n" + "="*80)
    print("UPDATING CONFIG PATHS")
    print("="*80 + "\n")
    
    config_content = '''"""
Configuration for Investment Comparison Analysis
Auto-detects correct paths and uses organized directory structure
"""
import os
from pathlib import Path

# Get the directory where this script is located
PROJECT_DIR = Path(__file__).parent.absolute()

# Data files - auto-detect in project directory
HOLDINGS_FILE = PROJECT_DIR / 'Demat Holding_NII_Trade_01.07.2025.xlsx'
HOLDINGS_SHEET = 'Demat Holding Report'

WEIGHTS_FILE = PROJECT_DIR / 'CURRENT_WEIGHATGE_(Aug 25).xlsx'
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

# NIFTY indices to compare (only NIFTY 50 now)
NIFTY_INDICES = {
    "NIFTY 50": "^NSEI",
}

# Debug info
if __name__ == "__main__":
    print("\\n" + "="*80)
    print("CONFIGURATION CHECK")
    print("="*80)
    print(f"\\nProject Directory: {PROJECT_DIR}")
    print(f"\\nData Files:")
    print(f"  Holdings: {HOLDINGS_FILE}")
    print(f"    Exists: {HOLDINGS_FILE.exists()}")
    print(f"  Weights:  {WEIGHTS_FILE}")
    print(f"    Exists: {WEIGHTS_FILE.exists()}")
    print(f"\\nDirectories:")
    print(f"  Data:    {DATA_DIR}")
    print(f"  Output:  {OUTPUT_DIR}")
    print(f"  Reports: {REPORTS_DIR}")
    print("="*80 + "\\n")
'''
    
    with open('config.py', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("✓ Updated config.py with new directory structure\n")


def update_data_scraper_paths():
    """Update data_scraper.py to use new data directory"""
    print("Updating data_scraper.py paths...")
    
    # Read current file
    with open('data_scraper.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update paths
    content = content.replace('DATA_DIR = "scraped_data"', 'DATA_DIR = "data/scraped_data"')
    
    # Write back
    with open('data_scraper.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Updated data_scraper.py\n")


def update_ticker_resolver_paths():
    """Update ticker_resolver.py to use new reports directory"""
    print("Updating ticker_resolver.py paths...")
    
    # Read current file
    with open('ticker_resolver.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update default parameter
    content = content.replace(
        "output_folder='ticker_reports'",
        "output_folder='reports/ticker_reports'"
    )
    
    # Write back
    with open('ticker_resolver.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Updated ticker_resolver.py\n")


def main():
    """Main reorganization workflow"""
    print("\n" + "="*80)
    print("PROJECT REORGANIZATION")
    print("="*80)
    print("\nThis will:")
    print("  1. Create organized directory structure")
    print("  2. Move existing data to proper directories")
    print("  3. Delete obsolete files")
    print("  4. Update file paths")
    print("\n" + "="*80)
    
    response = input("\nProceed with reorganization? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("\n❌ Reorganization cancelled\n")
        return
    
    # Execute reorganization
    create_directory_structure()
    move_existing_data()
    delete_obsolete_files()
    update_config_paths()
    update_data_scraper_paths()
    update_ticker_resolver_paths()
    show_final_structure()


if __name__ == "__main__":
    main()