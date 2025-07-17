# setup_package/config.py

# This file holds all your settings.

# --- Main Control Switch ---
# If True: The script will IGNORE the Colab ID and use `GLOBAL_VERSION`.
# If False: The script will read the Google Sheet using the ID and Tab Name below.
SWITCH = False # <-- Set to False to enable reading the Google Sheet

# --- Global Version Setting ---
# This is only used when SWITCH is True.
GLOBAL_VERSION = "0.0.6"

# --- Google Sheet Configuration ---
# This is only used when SWITCH is False.

# Find this ID in the URL of your Google Sheet.
# Example URL: https://docs.google.com/spreadsheets/d/THIS_IS_THE_ID/edit
SHEET_ID = "14neNkLpLNhtYntcv8vipyreP7y1aq16M9" # <-- REPLACE WITH YOUR ACTUAL SHEET ID

# The exact name of the tab (worksheet) inside your Google Sheet to read from.
# For example: "Sheet1", "Latest Working Version", "Autorun_Results"
SHEET_TAB_NAME = "Sheet1"
