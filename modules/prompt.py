import os
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Get Sheet ID from environment variables
SPREADSHEET_ID = os.getenv("SHEET_ID")

# Sheet Ranges
SHEET1_RANGE = "topics!A1:Z1000"
SHEET2_RANGE = "prompt!A1:Z1000"

# Config
MAX_REUSE_TIMES = 5
TOGGLE_COLUMN_NAME = "status"
LAST_USED_COLUMN_NAME = "last used"
TIMES_USED_COLUMN_NAME = "times used"
VALUE_INPUT_OPTION = "RAW"

# Google Sheets API Authentication
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Get the actual service account file path
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_FILE_PATH", "secrets/SERVICE_FILE.json")

# Ensure the file exists before using it
if not os.path.exists(SERVICE_ACCOUNT_FILE):
    raise FileNotFoundError(f"Service account file not found: {SERVICE_ACCOUNT_FILE}")

# Authenticate using the file
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Authorize with gspread and Google Sheets API
gc = gspread.authorize(creds)
service = build("sheets", "v4", credentials=creds)

def get_sheet_data(sheet_range):
    """Fetch data from Google Sheets."""
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=sheet_range).execute()
    return result.get("values", [])

def update_sheet_data(sheet_range, values):
    """Update Google Sheets with new values."""
    body = {"values": values}
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range=sheet_range, valueInputOption=VALUE_INPUT_OPTION, body=body
    ).execute()

def sync_google_sheets_data():
    """Synchronize data between Sheet1 and Sheet2."""
    data1 = get_sheet_data(SHEET1_RANGE)
    data2 = get_sheet_data(SHEET2_RANGE)

    headers1 = data1[0]
    headers2 = data2[0]
    rows1 = data1[1:]
    rows2 = data2[1:]

    matching_columns = [col for col in headers1 if col in headers2]

    # Ensure required columns exist in Sheet1
    for col in [TOGGLE_COLUMN_NAME, LAST_USED_COLUMN_NAME]:
        if col not in headers1:
            headers1.append(col)
            for row in rows1:
                row.append("")

    toggle_index = headers1.index(TOGGLE_COLUMN_NAME)
    last_used_index = headers1.index(LAST_USED_COLUMN_NAME)

    # Ensure required columns exist in Sheet2
    if TIMES_USED_COLUMN_NAME not in headers2:
        headers2.append(TIMES_USED_COLUMN_NAME)
        for row in rows2:
            row.append("0")

    times_used_index = headers2.index(TIMES_USED_COLUMN_NAME)
    updated_row = None

    # Iterate over rows in Sheet1 to find a suitable row to copy
    for row1 in rows1:
        if row1[toggle_index] == "used":
            continue  # Skip rows already used

        found_suitable_row = False
        for row2 in rows2:
            current_times_used = int(row2[times_used_index]) if row2[times_used_index] else 0
            if current_times_used < MAX_REUSE_TIMES:
                # Copy matching column values
                for col in matching_columns:
                    index1, index2 = headers1.index(col), headers2.index(col)
                    row2[index2] = row1[index1]

                # Mark as used
                row1[toggle_index] = "used"
                row1[last_used_index] = "this"

                # Reset previous "this" in Sheet1
                for r in rows1:
                    if r[last_used_index] == "this" and r != row1:
                        r[last_used_index] = ""

                # Increment times used
                row2[times_used_index] = str(current_times_used + 1)
                updated_row = row2
                found_suitable_row = True
                break
        
        if found_suitable_row or updated_row:
            break

    # Update Sheet1 and Sheet2 with modified data
    update_sheet_data(SHEET1_RANGE, [headers1] + rows1)
    update_sheet_data(SHEET2_RANGE, [headers2] + rows2)

    return ",".join(updated_row) if updated_row else ""

# Run the function
if __name__ == "__main__":
    result = sync_google_sheets_data()
    print("Updated Row:", result)
