from setuptools import setup, find_packages
import os

def get_version():
    """Read version from __init__.py"""
    version_file = os.path.join(os.path.dirname(__file__), 'setup_package', '__init__.py')
    try:
        with open(version_file, 'r') as f:
            for line in f:
                if line.startswith('__version__'):
                    # Extract version from line like: __version__ = "0.0.1"
                    version = line.split('=')[1].strip().strip('"').strip("'")
                    return version
    except Exception:
        pass
    return "0.0.1"

setup(
    name="Setup-Package",
    version=get_version(),
    packages=find_packages(),
    install_requires=[
        "google-auth",
        "google-auth-oauthlib", 
        "google-auth-httplib2",
        "google-api-python-client",
    ],
    author="Saad",
    description="API setup automation for Colab notebooks",
    url="https://github.com/Mohsin-h27/Setup_Package.git",
    python_requires='>=3.6',
)
