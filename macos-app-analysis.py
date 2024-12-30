import os
import subprocess
from datetime import datetime, timedelta
import platform
import plistlib
import json

class MacApplicationCleaner:
    def __init__(self, output_file='app_analysis.json'):
        """
        Initialize the MacOS Application Analyzer
        """
        self.applications_dir = '/Applications'
        self.user_applications_dir = os.path.expanduser('~/Applications')
        self.output_file = output_file
        self.app_candidates = []

    def get_last_used_date(self, app_path):
        """
        Retrieve the last used date for an application
        """
        try:
            # Use macOS-specific command to get last used date
            cmd = f'mdls -name kMDItemLastUsedDate "{app_path}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.stdout.strip():
                # Parse the date from the output
                date_str = result.stdout.split('=')[1].strip().strip('"')
                return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S %z')
        except Exception:
            pass
        return None

    def analyze_applications(self):
        """
        Analyze applications in both system and user application directories
        """
        search_dirs = [
            self.applications_dir, 
            self.user_applications_dir
        ]

        for directory in search_dirs:
            if not os.path.exists(directory):
                continue

            for item in os.listdir(directory):
                if item.endswith('.app'):
                    full_path = os.path.join(directory, item)
                    app_info = self.analyze_single_app(full_path)
                    if app_info:
                        self.app_candidates.append(app_info)

    def analyze_single_app(self, app_path):
        """
        Perform detailed analysis on a single application
        """
        try:
            # Basic file system information
            file_stats = os.stat(app_path)
            creation_time = datetime.fromtimestamp(file_stats.st_ctime)
            
            # Last used date
            last_used = self.get_last_used_date(app_path)
            
            # Try to extract app bundle information
            info_plist_path = os.path.join(app_path, 'Contents', 'Info.plist')
            app_name = os.path.splitext(os.path.basename(app_path))[0]
            bundle_identifier = None
            version = None

            try:
                with open(info_plist_path, 'rb') as f:
                    plist_data = plistlib.load(f)
                    bundle_identifier = plist_data.get('CFBundleIdentifier')
                    version = plist_data.get('CFBundleShortVersionString')
            except Exception:
                pass

            # Deletion criteria
            deletion_score = 0
            reasons = []

            # Criteria 1: Not used in the last year
            if not last_used or (datetime.now() - last_used) > timedelta(days=365):
                deletion_score += 30
                reasons.append("Not used in over a year")

            # Criteria 2: Very old application
            if (datetime.now() - creation_time) > timedelta(days=730):  # 2 years
                deletion_score += 20
                reasons.append("Installed over 2 years ago")

            # Criteria 3: Small or potentially redundant applications
            app_size = sum(os.path.getsize(os.path.join(dirpath,filename)) 
                           for dirpath, _, filenames in os.walk(app_path) 
                           for filename in filenames)
            
            if app_size < 10*1024*1024:  # Less than 10MB
                deletion_score += 10
                reasons.append("Very small application size")

            # Criteria 4: Check for duplicate/redundant apps
            if any(x in app_name.lower() for x in ['demo', 'trial', 'beta', 'old']):
                deletion_score += 15
                reasons.append("Potentially outdated or trial version")

            # If we have a significant deletion score, consider it a candidate
            if deletion_score >= 30:
                return {
                    'name': app_name,
                    'path': app_path,
                    'bundle_id': bundle_identifier,
                    'version': version,
                    'creation_date': creation_time.isoformat(),
                    'last_used': last_used.isoformat() if last_used else None,
                    'size_bytes': app_size,
                    'deletion_score': deletion_score,
                    'reasons': reasons
                }
            
            return None

        except Exception as e:
            print(f"Error analyzing {app_path}: {e}")
            return None

    def save_results(self):
        """
        Save analysis results to a JSON file
        """
        if self.app_candidates:
            with open(self.output_file, 'w') as f:
                json.dump(self.app_candidates, f, indent=2)
            print(f"Analysis saved to {self.output_file}")
        else:
            print("No applications found as deletion candidates.")

    def print_candidates(self):
        """
        Print detailed information about deletion candidates
        """
        if not self.app_candidates:
            print("No applications found as deletion candidates.")
            return

        print("\n=== Application Deletion Candidates ===")
        for app in self.app_candidates:
            print(f"\nApplication: {app['name']}")
            print(f"Path: {app['path']}")
            print(f"Version: {app.get('version', 'Unknown')}")
            print(f"Creation Date: {app['creation_date']}")
            print(f"Last Used: {app.get('last_used', 'Never')}")
            print(f"Size: {app['size_bytes'] / 1024 / 1024:.2f} MB")
            print("Deletion Reasons:")
            for reason in app['reasons']:
                print(f"  - {reason}")
            print(f"Deletion Score: {app['deletion_score']}")

def main():
    # Check macOS
    if platform.system() != 'Darwin':
        print("This script is designed for macOS only.")
        return

    # Require confirmation (safety check)
    print("⚠️  WARNING: This script will analyze applications for potential deletion.")
    print("It is strongly recommended to backup your system before taking any actions.")
    
    confirm = input("Do you want to continue? (yes/no): ").lower()
    if confirm != 'yes':
        print("Operation cancelled.")
        return

    cleaner = MacApplicationCleaner()
    cleaner.analyze_applications()
    cleaner.print_candidates()
    cleaner.save_results()

if __name__ == "__main__":
    main()
```

Key Features of the Script:

1. **Deletion Criteria**:
   - Not used in over a year
   - Installed more than 2 years ago
   - Very small application size
   - Potential trial/demo/beta versions

2. **Analysis Includes**:
   - Application name
   - Full path
   - Bundle identifier
   - Version
   - Creation date
   - Last used date
   - Application size
   - Reasons for potential deletion

3. **Safety Measures**:
   - Confirmation prompt before analysis
   - Only works on macOS
   - Saves results to a JSON file for review

4. **Output**:
   - Prints detailed candidates to console
   - Saves full details to `app_analysis.json`

### Usage Notes
- Run with Python 3
- Requires macOS
- Recommend running with sudo for full system access
- Always backup before deleting applications

### Recommended Next Steps
1. Review the generated `app_analysis.json`
2. Manually verify applications before deletion
3. Use macOS's built-in uninstaller or App Cleaner

Would you like me to explain any part of the script in more detail?