import os
import shutil
from pathlib import Path

def move_optional_utilities(
    base_path=r"C:\Users\swaga\OneDrive\Desktop\nifty_comparision",
    tools_folder_name="tools"
):
    """
    Moves all optional utility scripts into a 'tools' subdirectory.
    Creates the folder if it doesn't exist.
    """
    # List of optional utility files
    optional_files = [
        "auto_detect_files.py",
        "detect_sheets.py",
        "data_scraper.py",
        "fix_syntax_errors.py"
    ]
    
    base_dir = Path(base_path)
    tools_dir = base_dir / tools_folder_name
    tools_dir.mkdir(exist_ok=True)

    print(f"\n📁 Organizing optional utilities into: {tools_dir.resolve()}\n")

    for filename in optional_files:
        src = base_dir / filename
        dest = tools_dir / filename
        
        if src.exists():
            shutil.move(str(src), str(dest))
            print(f"  ✓ Moved: {filename} → {tools_folder_name}/")
        else:
            print(f"  ⚠️  Skipped (not found): {filename}")

    print("\n✅ All optional utilities have been organized!\n")


if __name__ == "__main__":
    move_optional_utilities()
