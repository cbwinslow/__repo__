import subprocess
import sys
from urllib.parse import urlparse
import logging
from time import sleep

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_valid_url(url):
    """Check if the given string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def process_url(url, exe_path):
    """Process a single URL using the provided executable."""
    try:
        result = subprocess.run([exe_path, url], capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            logging.info(f"Successfully processed URL: {url}")
        else:
            logging.error(f"Error processing URL: {url}. Error: {result.stderr}")
    except subprocess.TimeoutExpired:
        logging.warning(f"Timeout while processing URL: {url}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error calling executable for URL: {url}. Error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error while processing URL: {url}. Error: {str(e)}")

def main(url_file, exe_path):
    """Main function to process URLs from a file."""
    try:
        with open(url_file, 'r') as file:
            for line in file:
                url = line.strip()
                if not url:
                    continue
                if not is_valid_url(url):
                    logging.warning(f"Invalid URL skipped: {url}")
                    continue
                process_url(url, exe_path)
                sleep(1)  # Add a small delay between processing URLs
    except FileNotFoundError:
        logging.error(f"URL file not found: {url_file}")
    except PermissionError:
        logging.error(f"Permission denied when trying to read file: {url_file}")
    except Exception as e:
        logging.error(f"Unexpected error while reading URL file: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <url_file> <exe_path>")
        sys.exit(1)
    
    url_file = sys.argv[1]
    exe_path = sys.argv[2]
    main(url_file, exe_path)