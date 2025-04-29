from modules.script_generation import script_generation

# Hardcoded input values
SHEET1_NAME = "topics"
SHEET3_NAME = "response"

def update_google_sheets(sh):
    # Step 1: Generate script data
    json_response = script_generation()
    print(json_response)
    description = json_response.get("description", "")
    script_data = json_response.get("script", [])

    # Open the spreadsheet
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
    
    print("Step 2 -Google Sheets updated successfully!")

# Run the function
if __name__ == "__main__":
    update_google_sheets()
    print("Step 1 - 3 completed successfully!")

