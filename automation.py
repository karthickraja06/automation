# automation.py
import datetime
from modules.organize import update_google_sheets
from modules.image_prompt import image_prompt_organize 

def run_task():

    print(f"Automation running at {datetime.datetime.now()}")
    update_google_sheets()
    print("Script completed.")
    image_prompt_organize()
    print("Img prompt generate completed.")


if __name__ == "__main__":
    run_task()
