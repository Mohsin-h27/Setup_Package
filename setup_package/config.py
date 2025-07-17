# setup_package/config.py
# --- Main Control Switch ---
# If True: The script will automatically use the `GLOBAL_VERSION` below.
# If False: The script will ask for a Colab ID and use the `VERSION_MAPPING`.
SWITCH = True

# --- Global Version Setting ---
# This is the version of the API FILES that will be installed when SWITCH is True.
GLOBAL_VERSION = "0.0.8"

# --- Specific Version Mapping ---
# This dictionary maps a Colab ID to a specific API version.
# This is only used when SWITCH is False.
VERSION_MAPPING = {
    '1001': '0.0.4',
    '1002': '0.0.8',
    '1003': '0.0.1',
    # Add more Colab IDs and their corresponding versions here
}
