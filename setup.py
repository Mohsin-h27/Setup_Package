from setuptools import setup, find_packages
import os

def get_version():
    """
    Reads the version of the package from setup_package/__init__.py.
    """
    version_file = os.path.join(os.path.dirname(__file__), 'setup_package', '__init__.py')
    try:
        with open(version_file, 'r') as f:
            for line in f:
                if line.startswith('__version__'):
                    version = line.split('=')[1].strip().strip('"').strip("'")
                    return version
    except FileNotFoundError:
        raise RuntimeError(f"The file {version_file} was not found.")
    
    raise RuntimeError("Unable to find __version__ string in __init__.py.")

setup(
    name="Setup-Package",
    version=get_version(),
    packages=find_packages(),
    install_requires=[
        "google-auth",
        "google-auth-oauthlib", 
        "google-auth-httplib2",
        "google-api-python-client",
        "gspread",  # <-- Required for Google Sheets
    ],
    author="Mohsin",
    description="API setup automation for Colab notebooks",
    url="https://github.com/Mohsin-h27/Setup_Package.git",
    python_requires='>=3.6',
)
