# automation.py
import datetime
from modules.organize import update_google_sheets
from modules.image_prompt import image_prompt_organize 
from modules.image_generation import image_generation
from modules.audio_generation import audio_generation
def run_task():

    print(f"Automation running at {datetime.datetime.now()}")
    update_google_sheets()
    print("Script completed.")
    audio_generation()
    print("Audio generation completed.")
    image_prompt_organize()
    print("Img prompt generate completed.")
    image_generation()
    print("Image generation completed.")

if __name__ == "__main__":
    run_task()
