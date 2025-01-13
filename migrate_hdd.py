import os
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Constants
BACKUP_FOLDER = "Backup_{date}".format(date=datetime.now().strftime("%Y%m%d_%H%M%S"))

def create_backup(source_paths, backup_path):
    """
    Creates a backup of the specified source files/folders to a backup directory.
    """
    try:
        backup_dir = Path(backup_path) / BACKUP_FOLDER
        backup_dir.mkdir(parents=True, exist_ok=True)

        for source in source_paths:
            src = Path(source)
            if src.exists():
                dest = backup_dir / src.name
                if src.is_dir():
                    shutil.copytree(src, dest)
                else:
                    shutil.copy2(src, dest)
                print(f"Backed up: {src} -> {dest}")
            else:
                print(f"Warning: Source path does not exist: {src}")
        return backup_dir
    except Exception as e:
        print(f"Error during backup: {e}")
        sys.exit(1)

def migrate_files(source_paths, target_path):
    """
    Migrates files and directories from source to target while preserving directory structure.
    """
    try:
        target_dir = Path(target_path)
        target_dir.mkdir(parents=True, exist_ok=True)
        for source in source_paths:
            src = Path(source)
            if not src.exists():
                print(f"Error: Source path does not exist: {src}")
                continue
            dest = target_dir / src.name
            if src.is_dir():
                shutil.copytree(src, dest)
            else:
                shutil.copy2(src, dest)
            print(f"Migrated: {src} -> {dest}")
        return target_dir
    except Exception as e:
        print(f"Error during migration: {e}")
        sys.exit(1)

def create_symlinks(source_paths, target_path):
    """
    Creates symbolic links for migrated files and directories.
    """
    for source in source_paths:
        src = Path(source)
        if not src.exists():
            print(f"Warning: Source path does not exist: {src}")
            continue
        symlink_path = src
        target = Path(target_path) / src.name
        try:
            src.unlink()  # Remove existing file/directory
            symlink_path.symlink_to(target, target.is_dir())
            print(f"Symlink created: {symlink_path} -> {target}")
        except Exception as e:
            print(f"Error creating symlink for {src}: {e}")

def update_environment_variables(env_vars, target_path):
    """
    Updates environment variables pointing to the new file locations.
    """
    for var, original_path in env_vars.items():
        new_path = str(Path(target_path) / Path(original_path).name)
        os.environ[var] = new_path
        print(f"Updated environment variable {var}: {original_path} -> {new_path}")

def clean_up(source_paths):
    """
    Cleans up the original files/directories after successful migration.
    """
    for source in source_paths:
        src = Path(source)
        try:
            if src.is_dir():
                shutil.rmtree(src)
            else:
                src.unlink()
            print(f"Cleaned up: {src}")
        except Exception as e:
            print(f"Error cleaning up {src}: {e}")

def main():
    # Prompt user for backup and migration paths
    print("Backup and Migration Script")
    backup_path = input("Enter the path for backups (e.g., a Google Drive mount): ").strip()
    target_path = input("Enter the target path for migration (e.g., internal SSD): ").strip()

    # Get paths to back up and migrate
    source_paths = input("Enter the paths to back up and migrate (comma-separated): ").split(",")

    # Backup Phase
    print("\nStarting backup...")
    backup_dir = create_backup(source_paths, backup_path)
    print(f"Backup completed: {backup_dir}\n")

    # Migration Phase
    print("Starting migration...")
    target_dir = migrate_files(source_paths, target_path)
    print(f"Migration completed: {target_dir}\n")

    # Create Symlinks
    print("Creating symbolic links...")
    create_symlinks(source_paths, target_path)

    # Update Environment Variables
    print("Updating environment variables...")
    env_vars = {
        # Replace with actual environment variables to update
        "EXAMPLE_VAR": source_paths[0]
    }
    update_environment_variables(env_vars, target_path)

    # Clean Up
    print("Cleaning up original files...")
    clean_up(source_paths)

    print("Process completed successfully!")

if __name__ == "__main__":
    main()
