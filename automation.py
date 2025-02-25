# automation.py
import datetime
from modules.organize import update_google_sheets
#from modules.audio_generation import audio_generation  
def run_task():
    print(f"Automation running at {datetime.datetime.now()}")
    update_google_sheets()
    print("Script completed.")
    #audio_generation()
    #print("Voice generate completed.")


if __name__ == "__main__":
    run_task()
