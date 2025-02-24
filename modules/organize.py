import os
import gspread
from google.oauth2.service_account import Credentials
from modules.script_generation import script_generation

# Hardcoded input values
SPREADSHEET_ID = os.getenv("SHEET_ID")
SHEET1_NAME = "topics"
SHEET3_NAME = "response"

# Authenticate with Google Sheets API
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
service_file_path = os.getenv("SERVICE_FILE_PATH", "secrets/SERVICE_FILE.json")

if not service_file_path or not os.path.exists(service_file_path):
        raise ValueError("Missing or invalid SERVICE_FILE_PATH")

creds = Credentials.from_service_account_file(service_file_path, scopes=SCOPES)
gc = gspread.authorize(creds)

def update_google_sheets():
    # Step 1: Generate script data
    json_response = script_generation()
    description = json_response[0].get("video_description", "")
    script_data = json_response[0].get("script", [])
    
    # Open the spreadsheet
    sh = gc.open_by_key(SPREADSHEET_ID)
    sheet1 = sh.worksheet(SHEET1_NAME)
    sheet3 = sh.worksheet(SHEET3_NAME)
    
    # Step 2: Find the row with 'this' under 'last used' column in Sheet1
    sheet1_data = sheet1.get_all_values()
    header = sheet1_data[0]  # Assuming first row is header
    last_used_col_index = header.index("last used")
    description_col_index = header.index("description")
    
    for i, row in enumerate(sheet1_data[1:], start=2):
        if row[last_used_col_index].lower() == "this":
            sheet1.update_cell(i, description_col_index + 1, description)
            break

    # Get only the first row (header)
    sheet3_header = sheet3.row_values(1)
    sheet3.clear()
    sheet3.append_row(sheet3_header)  # Re-add the header row

    if script_data:
        for entry in script_data:
            sheet3.append_row([entry.get("name", ""), entry.get("gender", ""), entry.get("dialogue", "")])
    
    print("Google Sheets updated successfully!")

# Run the function
if __name__ == "__main__":
    update_google_sheets()
    print("Script completed.")

