import datetime
import subprocess

def generate_version():
    # Get the current date and time
    now = datetime.datetime.now()
    
    # Extract year, month, and day components
    year = str(now.year)[-2:]  # Extract the last two digits of the year
    month = str(now.month).zfill(2)  # Zero-pad the month to ensure two digits
    day = str(now.day).zfill(2)  # Zero-pad the day to ensure two digits
    
    # Get the number of commits
    try:
        commit_count = int(subprocess.check_output(["git", "rev-list", "--count", "HEAD"]))
    except Exception as e:
        print(f"Error: {e}")
        commit_count = 0
    
    # Concatenate the components to form the version number
    version = f"{year}.{month}.{day}.{commit_count}"
    
    return version

if __name__ == "__main__":
    version = generate_version()
    print(f"Generated version number: {version}")
