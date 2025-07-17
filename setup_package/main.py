# setup_package/main.py

import io
import os
import sys
import zipfile
import shutil

# Imports for Google APIs and Sheets
from google.colab import auth
from google.auth import default
import gspread
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Import your settings from the config.py file
from .config import SWITCH, GLOBAL_VERSION, SHEET_ID

def _get_mapping_from_sheet():
    """
    Connects to Google Sheets using its ID, reads the version data, and builds
    the version mapping dictionary dynamically.
    """
    print(f"Reading version mapping from Google Sheet ID: '{SHEET_ID}'...")
    try:
        # This authenticates the user and gets credentials for Google APIs.
        creds, _ = default()
        gc = gspread.authorize(creds)
        
        # Open the sheet by its unique ID and get all records from the first tab.
        worksheet = gc.open_by_key(SHEET_ID).sheet1
        records = worksheet.get_all_records()
        
        dynamic_mapping = {}
        for record in records:
            notebook_filename = record.get('Notebook')
            version = record.get('Latest_Working_Version')

            if notebook_filename and version:
                # Parsing logic: "Agent-1000_base-Merged.ipynb" -> "1000_base"
                parts = notebook_filename.split('-')
                if len(parts) > 1:
                    colab_id = parts[1]
                    dynamic_mapping[colab_id] = str(version)
        
        print(f"Successfully built mapping for {len(dynamic_mapping)} notebooks from sheet.")
        return dynamic_mapping

    except gspread.exceptions.SpreadsheetNotFound:
        print(f"\n❌ Error: The Google Sheet with ID '{SHEET_ID}' was not found.")
        print("Please ensure the ID in config.py is correct and that you have shared the sheet.")
        sys.exit("Setup aborted: Spreadsheet not found.")
    except Exception as e:
        print(f"\n❌ Error: Could not read or process the Google Sheet: {e}")
        sys.exit("Setup aborted: Failed to get version mapping from sheet.")


def run_setup(version: str):
    """
    This function performs the actual installation of files from Google Drive.
    """
    print(f"--- Starting Setup for Version {version} ---")
    CONTENT_DIR = '/content'
    APIS_DIR = os.path.join(CONTENT_DIR, 'APIs')
    DBS_DIR = os.path.join(CONTENT_DIR, 'DBs')
    SCRIPTS_DIR = os.path.join(CONTENT_DIR, 'Scripts')
    FC_DIR = os.path.join(CONTENT_DIR, 'Schemas')
    ZIP_PATH = os.path.join(CONTENT_DIR, f'APIs_V{version}.zip')
    APIS_FOLDER_ID = '1QpkAZxXhVFzIbm8qPGPRP1YqXEvJ4uD4'
    ITEMS_TO_EXTRACT = ['APIs/', 'DBs/', 'Scripts/']
    print("Cleaning up previous installation...")
    for path in [APIS_DIR, DBS_DIR, SCRIPTS_DIR, FC_DIR, ZIP_PATH]:
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
    auth.authenticate_user()
    drive_service = build('drive', 'v3')
    def download_drive_file(service, file_id, output_path, show_progress=True):
        request = service.files().get_media(fileId=file_id)
        with io.FileIO(output_path, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                if show_progress:
                    print(f"\rDownload progress: {int(status.progress() * 100)}%", end="")
            print("\nDownload complete.")
    print(f"Searching for APIs zip file with version {version} in Drive...")
    apis_file_id = None
    try:
        query = f"'{APIS_FOLDER_ID}' in parents and trashed=false"
        results = drive_service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])
        for file in files:
            file_name = file.get('name', '')
            if file_name.lower() == f'apis_v{version.lower()}.zip':
                apis_file_id = file.get('id')
                print(f"Found matching file: {file_name} (ID: {apis_file_id})")
                break
    except Exception as e:
        print(f"An error occurred while listing files in Google Drive: {e}")
    if not apis_file_id:
        print(f"Error: Could not find APIs zip file with version {version} in the specified folder.")
        sys.exit("Required APIs zip file not found.")
    print(f"Downloading APIs zip file...")
    download_drive_file(drive_service, apis_file_id, ZIP_PATH)
    print(f"Extracting items from {ZIP_PATH}...")
    try:
        with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
            for member in zip_ref.namelist():
                for item_prefix in ITEMS_TO_EXTRACT:
                    if member.startswith(item_prefix):
                        zip_ref.extract(member, CONTENT_DIR)
                        break
    except Exception as e:
        print(f"An error occurred during extraction: {e}")
        sys.exit("Extraction failed.")
    if os.path.exists(ZIP_PATH):
        os.remove(ZIP_PATH)
    if os.path.exists(APIS_DIR):
        sys.path.append(APIS_DIR)
    else:
        print(f"Error: APIS directory not found at {APIS_DIR} after extraction.")
    print("\nVerifying extracted items:")
    all_present = True
    for path in [APIS_DIR, DBS_DIR, SCRIPTS_DIR]:
        if os.path.exists(path):
            print(f"✅ {os.path.basename(path)} is present.")
        else:
            print(f"❌ {os.path.basename(path)} is MISSING!")
            all_present = False
    if not all_present:
        print("\n❌ Setup failed! Not all required items were extracted.")
        sys.exit("Verification failed.")
    try:
        from Scripts.FCSpec import generate_package_schema
        print("\nGenerating FC Schemas...")
        os.makedirs(FC_DIR, exist_ok=True)
        os.chdir(APIS_DIR)
        for package_name in os.listdir(APIS_DIR):
            package_path = os.path.join(APIS_DIR, package_name)
            if os.path.isdir(package_path):
                generate_package_schema(package_path, output_folder_path=FC_DIR)
        print(f"✅ Successfully generated {len(os.listdir(FC_DIR))} FC Schemas to {FC_DIR}")
    except ImportError:
        print("\nSkipping Schema generation: 'Scripts/FCSpec.py' not found.")
    except Exception as e:
        print(f"\nAn error occurred during Schema generation: {e}")
    finally:
        os.chdir(CONTENT_DIR)
    print(f"\n🎉 All setup complete! Version {version} is ready to use.")


def main(colab_id: str = None):
    """
    Main entry point. Decides which version to use based on config.py.
    """
    version_to_use = None
    if SWITCH:
        version_to_use = GLOBAL_VERSION
        print(f"Global switch is ON. Using global version: {version_to_use}")
    else:
        VERSION_MAPPING = _get_mapping_from_sheet()
        
        if not colab_id:
            print("\n❌ Error: Switch is OFF but no Colab ID was provided.")
            sys.exit("Setup aborted: Missing Colab ID.")
            
        print(f"Global switch is OFF. Checking for Colab ID '{colab_id}' in sheet mapping.")
        if colab_id in VERSION_MAPPING:
            version_to_use = VERSION_MAPPING[colab_id]
            print(f"Found version in sheet: {version_to_use}")
        else:
            print(f"\n❌ Error: Colab ID '{colab_id}' not found in the Google Sheet mapping.")
            sys.exit("Setup aborted: Invalid Colab ID.")
    
    if version_to_use:
        run_setup(version=version_to_use)
    else:
        print("Error: Could not determine a version to use.")
        sys.exit("Setup aborted.")
