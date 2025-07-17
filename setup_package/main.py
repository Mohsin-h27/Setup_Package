# setup_package/main.py

import io
import os
import sys
import zipfile
import shutil
from google.colab import auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Import your settings from the config.py file
from .config import SWITCH, GLOBAL_VERSION, VERSION_MAPPING

def run_setup(version: str):
    """
    This function performs the actual installation. It takes a version number
    and installs the corresponding files from Google Drive.
    
    Args:
        version (str): The specific API version to set up (e.g., "0.0.8").
    """
    print(f"--- Starting Setup for Version {version} ---")

    # Define all necessary paths and constants
    CONTENT_DIR = '/content'
    APIS_DIR = os.path.join(CONTENT_DIR, 'APIs')
    DBS_DIR = os.path.join(CONTENT_DIR, 'DBs')
    SCRIPTS_DIR = os.path.join(CONTENT_DIR, 'Scripts')
    FC_DIR = os.path.join(CONTENT_DIR, 'Schemas')
    ZIP_PATH = os.path.join(CONTENT_DIR, f'APIs_V{version}.zip')
    APIS_FOLDER_ID = '1QpkAZxXhVFzIbm8qPGPRP1YqXEvJ4uD4'
    ITEMS_TO_EXTRACT = ['APIs/', 'DBs/', 'Scripts/']

    # Clean up any previous installation to ensure a fresh start
    print("Cleaning up previous installation...")
    for path in [APIS_DIR, DBS_DIR, SCRIPTS_DIR, FC_DIR, ZIP_PATH]:
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)

    # Authenticate with Google to access Drive
    auth.authenticate_user()
    drive_service = build('drive', 'v3')

    # Helper function to show download progress
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

    # 1. Find the correct zip file in your Google Drive folder
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

    # 2. Download the found zip file
    print(f"Downloading APIs zip file...")
    download_drive_file(drive_service, apis_file_id, ZIP_PATH)

    # 3. Extract the contents from the zip file
    print(f"Extracting items from {ZIP_PATH}...")
    try:
        with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
            for member in zip_ref.namelist():
                for item_prefix in ITEMS_TO_EXTRACT:
                    if member.startswith(item_prefix):
                        zip_ref.extract(member, CONTENT_DIR)
                        break
    except zipfile.BadZipFile:
        print(f"Error: The downloaded file at {ZIP_PATH} is not a valid zip file.")
        sys.exit("Invalid zip file downloaded.")
    except Exception as e:
        print(f"An error occurred during extraction: {e}")
        sys.exit("Extraction failed.")

    # 4. Clean up by deleting the downloaded zip file
    if os.path.exists(ZIP_PATH):
        os.remove(ZIP_PATH)

    # 5. Add the new APIs folder to the system path so Python can find it
    if os.path.exists(APIS_DIR):
        sys.path.append(APIS_DIR)
    else:
        print(f"Error: APIS directory not found at {APIS_DIR} after extraction.")

    # 6. Verify that the main folders were extracted correctly
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

    # 7. Generate Schemas if the script for it exists
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


def main():
    """
    This is the main entry point you call from your Colab notebook.
    It decides which version to use based on your config.py settings,
    and then it calls run_setup() to do the installation.
    """
    
    version_to_use = None
    # This block implements your requested logic exactly.
    if SWITCH:
        # If the switch is on, use the global version automatically.
        version_to_use = GLOBAL_VERSION
        print(f"Global switch is ON. Using global version: {version_to_use}")
    else:
        # If the switch is off, ask the user for the Colab ID.
        print("Global switch is OFF. Please provide the Colab ID.")
        try:
            colab_id = input("Enter the Colab ID for this notebook: ")
            if colab_id in VERSION_MAPPING:
                # If the ID is found in the mapping, use that version.
                version_to_use = VERSION_MAPPING[colab_id]
                print(f"Found version for Colab ID '{colab_id}': {version_to_use}")
            else:
                # If the ID is not found, print an error and stop the script.
                # This enforces your rule: "if not version than not run that colab"
                print(f"\n❌ Error: Colab ID '{colab_id}' not found in the version mapping.")
                print("Please add the ID to 'setup_package/config.py' or check for typos.")
                sys.exit("Setup aborted: Invalid Colab ID.")
        except KeyboardInterrupt:
            print("\nSetup cancelled by user.")
            sys.exit()
    
    # After figuring out the version, call the setup function to do the work.
    if version_to_use:
        run_setup(version=version_to_use)
    else:
        # This case should not be reached due to the sys.exit calls above, but it's here for safety.
        print("Error: Could not determine a version to use.")
        sys.exit("Setup aborted.")
