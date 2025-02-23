# automation.py
import datetime
from modules.organize import update_google_sheets
from modules.audio_generation import generate_speech  
def run_task():
    print(f"Automation running at {datetime.datetime.now()}")
    update_google_sheets()
    print("Script completed.")
    generate_speech()
    print("Voice generate completed.")


if __name__ == "__main__":
    run_task()
