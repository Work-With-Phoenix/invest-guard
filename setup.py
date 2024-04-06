from setuptools import setup, find_packages
import subprocess

# Function to generate version dynamically
def generate_version():
    try:
        version = subprocess.check_output(["python", "generate_version.py"], universal_newlines=True).strip()
    except Exception as e:
        print(f"Error generating version: {e}")
        version = "0.0.1"  # Default version
    return version

# Call the generate_version function to get the version
version = generate_version()

setup(
    name="invest_guard",
    version=version,
    packages=find_packages(),
    # Include other setup configurations as needed
)
