"""
PROJECT CLEANUP SCRIPT
Removes unnecessary, duplicate, and old files
Keeps only essential files for the project
"""
import os
import shutil


# ========================================
# CORE PROJECT FILES (KEEP THESE)
# ========================================
ESSENTIAL_FILES = {
    # Core modules
    'main.py',
    'config.py',
    'data_loader.py',
    'data_scraper.py',
    'ticker_resolver.py',
    'validated_tickers.py',
    'smart_calculator.py',
    'visualizer.py',
    'market_data.py',
    
    # Utility scripts
    'nse_equity_matcher.py',
    'fix_syntax_errors.py',
    'cleanup.py',
    
    # Configuration
    'requirements.txt',
    
    # Data files
    'CURRENT_WEIGHATGE_(Aug 25)',
    'Demat Holding_NII_Trade_01.07.2025',
    'EQUITY_L.csv',
    
    # Documentation (optional - can delete if not needed)
    'README.md',
}

# ========================================
# FILES TO DELETE
# ========================================
OBSOLETE_FILES = [
    # Old documentation (excessive)
    'DELIVERY_CHECKLIST.md',
    'DELIVERY_SUMMARY.md',
    'FILE_LIST.txt',
    'INSTALLATION.md',
    'OUTPUT_EXAMPLES.md',
    'PROJECT_STRUCTURE.txt',
    'PROJECT_SUMMARY.md',
    'QUICKSTART.md',
    'QUICK_START.md',
    'START_HERE.txt',
    
    # Duplicate/old calculators
    'calculator.py',  # Replaced by smart_calculator.py
    'portfolio_calculator.py',  # Old version
    
    # Duplicate/old data fetchers
    'stock_scraper.py',  # Old version, replaced by data_scraper.py
    'nifty_data.py',  # Old version
    
    # Duplicate visualizers
    'visualization.py',  # Old version, replaced by visualizer.py
    
    # Old utility scripts (replaced by better versions)
    'manual_mapper.py',  # Old version
    'auto_update_tickers.py',  # Replaced by nse_equity_matcher.py
    'validate_yahoo_tickers.py',  # Replaced by nse_equity_matcher.py
    'merge_yahoo_tickers.py',  # Not needed anymore
    'add_manual_mappings.py',  # One-time use, no longer needed
    
    # Old batch files
    'run.bat',
    'run_analysis.bat',
    
    # Archive/backup files
    'nifty_project_files.zip',
]

# ========================================
# DIRECTORIES TO CLEAN
# ========================================
CLEAN_DIRECTORIES = [
    '__pycache__',  # Python cache
    'price_cache',  # Old cache system
    '.pytest_cache',  # Test cache
    '.mypy_cache',  # Type checking cache
]


def safe_delete_file(filepath):
    """Safely delete a file with error handling"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
    except Exception as e:
        print(f"    ⚠️  Could not delete {filepath}: {e}")
        return False


def safe_delete_directory(dirpath):
    """Safely delete a directory with error handling"""
    try:
        if os.path.exists(dirpath):
            shutil.rmtree(dirpath)
            return True
        return False
    except Exception as e:
        print(f"    ⚠️  Could not delete {dirpath}: {e}")
        return False


def cleanup_project():
    """Main cleanup function"""
    
    print("\n" + "="*80)
    print("PROJECT CLEANUP")
    print("="*80)
    print("\nThis will remove obsolete, duplicate, and unnecessary files")
    print("Essential files will be preserved")
    
    # Show what will be deleted
    print("\n" + "-"*80)
    print("FILES TO BE DELETED:")
    print("-"*80)
    for f in OBSOLETE_FILES:
        status = "✓ exists" if os.path.exists(f) else "- not found"
        print(f"  {f:50s} {status}")
    
    print("\n" + "-"*80)
    print("DIRECTORIES TO BE DELETED:")
    print("-"*80)
    for d in CLEAN_DIRECTORIES:
        status = "✓ exists" if os.path.exists(d) else "- not found"
        print(f"  {d:50s} {status}")
    
    # Ask for confirmation
    print("\n" + "="*80)
    response = input("Proceed with cleanup? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("\n❌ Cleanup cancelled")
        return
    
    print("\n" + "="*80)
    print("CLEANING UP...")
    print("="*80 + "\n")
    
    # Delete files
    deleted_files = 0
    for filename in OBSOLETE_FILES:
        if safe_delete_file(filename):
            print(f"✓ Deleted: {filename}")
            deleted_files += 1
    
    # Delete directories
    deleted_dirs = 0
    for dirname in CLEAN_DIRECTORIES:
        if safe_delete_directory(dirname):
            print(f"✓ Deleted directory: {dirname}")
            deleted_dirs += 1
    
    print("\n" + "="*80)
    print("CLEANUP COMPLETE")
    print("="*80)
    print(f"\nDeleted: {deleted_files} files, {deleted_dirs} directories")
    
    # Show remaining files
    print("\n" + "-"*80)
    print("ESSENTIAL FILES KEPT:")
    print("-"*80)
    
    for f in sorted(os.listdir('.')):
        if os.path.isfile(f) and f.endswith('.py'):
            print(f"  ✓ {f}")
    
    print("\n" + "="*80)
    print("DIRECTORY STRUCTURE:")
    print("="*80)
    print("""
Clean project structure:
├── main.py                      # Main analysis script
├── config.py                    # Configuration
├── data_loader.py              # Load Excel data
├── data_scraper.py             # Download stock prices
├── ticker_resolver.py          # Resolve stock tickers
├── validated_tickers.py        # NSE ticker database
├── smart_calculator.py         # Portfolio calculations
├── visualizer.py               # Create charts
├── market_data.py              # NIFTY data
├── nse_equity_matcher.py       # Match to NSE list
├── fix_syntax_errors.py        # Fix syntax issues
├── cleanup.py                  # This script
├── requirements.txt            # Dependencies
├── EQUITY_L.csv                # NSE equity list
├── [Excel data files]          # Holdings data
│
├── scraped_data/               # Downloaded stock prices
│   ├── prices/                 # Individual stock CSVs
│   └── download_state.json     # Download tracking
│
├── ticker_reports/             # Analysis reports
│   ├── successful_tickers.csv
│   ├── failed_tickers.csv
│   └── coverage_report.csv
│
└── output/                     # Generated charts
    └── [HTML chart files]
    """)
    
    print("\n✅ Your project is now clean and organized!")
    print("\nNext steps:")
    print("  1. Run: python nse_equity_matcher.py  (if not done)")
    print("  2. Run: python main.py")
    print("="*80 + "\n")


def list_all_files():
    """List all files in current directory for review"""
    print("\n" + "="*80)
    print("CURRENT FILES IN PROJECT")
    print("="*80 + "\n")
    
    # Get all files
    all_files = []
    for f in os.listdir('.'):
        if os.path.isfile(f):
            size = os.path.getsize(f)
            size_kb = size / 1024
            all_files.append((f, size_kb))
    
    # Sort by name
    all_files.sort()
    
    # Categorize
    essential = []
    obsolete = []
    other = []
    
    for fname, size in all_files:
        if fname in ESSENTIAL_FILES:
            essential.append((fname, size))
        elif fname in OBSOLETE_FILES:
            obsolete.append((fname, size))
        else:
            other.append((fname, size))
    
    print("ESSENTIAL FILES:")
    for fname, size in essential:
        print(f"  ✓ {fname:50s} {size:>8.1f} KB")
    
    print(f"\nOBSOLETE FILES (will be deleted):")
    for fname, size in obsolete:
        print(f"  ✗ {fname:50s} {size:>8.1f} KB")
    
    print(f"\nOTHER FILES:")
    for fname, size in other:
        print(f"  ? {fname:50s} {size:>8.1f} KB")
    
    total_size = sum(s for _, s in all_files)
    obsolete_size = sum(s for _, s in obsolete)
    
    print(f"\n" + "-"*80)
    print(f"Total files: {len(all_files)}")
    print(f"Total size: {total_size:.1f} KB")
    print(f"Obsolete size: {obsolete_size:.1f} KB ({obsolete_size/total_size*100:.1f}%)")
    print("="*80 + "\n")


if __name__ == "__main__":
    # First show what's there
    list_all_files()
    
    # Then cleanup
    cleanup_project()