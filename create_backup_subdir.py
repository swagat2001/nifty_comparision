import os
import shutil
from pathlib import Path
from datetime import datetime

def backup_old_files(
    base_path=r"C:\Users\swaga\OneDrive\Desktop\nifty_comparision",
    files_to_backup=None,
    backup_dir_name="backup_old_files",
    move=False,
    add_timestamp=False
):
    """
    Create a backup subdirectory and copy/move old files into it with .backup extension.
    Args:
        base_path (str): Base directory containing the files.
        files_to_backup (list): List of filenames to back up.
        backup_dir_name (str): Name of the backup folder to create.
        move (bool): If True, move files instead of copying.
        add_timestamp (bool): If True, append a timestamp to backup filenames.
    """
    if files_to_backup is None:
        files_to_backup = [
            "main.py",
            "yahoo_tickers_failed.csv",
            "nse_matched_tickers.csv"
        ]
    
    base_dir = Path(base_path)
    backup_dir = base_dir / backup_dir_name
    backup_dir.mkdir(exist_ok=True)

    print(f"\n📁 Backup directory created (if not existed): {backup_dir}\n")

    for filename in files_to_backup:
        src = base_dir / filename
        if src.exists():
            timestamp = datetime.now().strftime("_%Y%m%d_%H%M%S") if add_timestamp else ""
            backup_name = f"{src.stem}.backup{timestamp}{src.suffix}"
            dest = backup_dir / backup_name
            
            if move:
                shutil.move(str(src), str(dest))
                action = "Moved"
            else:
                shutil.copy2(str(src), str(dest))
                action = "Copied"
            
            print(f"  ✓ {action}: {src.name} → {dest.name}")
        else:
            print(f"  ⚠️  File not found: {src}")

    print("\n✅ Backup process complete!\n")


if __name__ == "__main__":
    # Set move=True to move instead of copy
    # Set add_timestamp=True to append datetime to file name
    backup_old_files(move=False, add_timestamp=True)
