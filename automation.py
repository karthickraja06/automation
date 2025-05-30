# automation.py
import datetime
import os
import gspread
from google.oauth2.service_account import Credentials
from modules.organize import update_google_sheets
from modules.image_prompt import image_prompt_organize 
from modules.image_generation import image_generation
from modules.audio_generation import audio_generation
from modules.video_generation import video_generation
from dotenv import load_dotenv

load_dotenv()

# Authenticate with Google Sheets API
SHEET_ID = os.getenv("SHEET_ID")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
service_file_path = os.getenv("SERVICE_FILE", "secrets/SERVICE_FILE.json")

if not service_file_path or not os.path.exists(service_file_path):
    raise ValueError("Missing or invalid SERVICE_FILE_PATH")

creds = Credentials.from_service_account_file(service_file_path, scopes=SCOPES)
gc = gspread.authorize(creds)
sh = gc.open_by_key(SHEET_ID)

def run_task():
    print(f"Automation running at {datetime.datetime.now()}")
    update_google_sheets(sh)
    print("Step 3 - Script completed.")
    audio_generation(sh)
    print("Step 4 - Audio generation completed.")
    image_prompt_organize(sh)
    print("Step 5 - Image prompt generation completed.")
    image_generation(sh)
    print("Step 6 - Image generation completed.")
    video_generation(sh)
    print("Step 7 - Video generation completed.")

if __name__ == "__main__":
    run_task()
