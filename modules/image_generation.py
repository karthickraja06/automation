import os
import time
import gspread
from io import BytesIO
from google.oauth2.service_account import Credentials
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
from datetime import datetime

def image_generation():
    # Load API Key from .env
    load_dotenv()
    HUGGINGFACE_API_KEY = os.getenv("HF_TOKEN")

    # Initialize Hugging Face Inference Client
    client = InferenceClient(
        provider="hf-inference",
        api_key=HUGGINGFACE_API_KEY
    )

    # Google Sheet Credentials
    SHEET_ID = os.getenv("SHEET_ID")
    SHEET_NAME = "img_prompt"
    service_file_path = os.getenv("SERVICE_FILE_PATH", "secrets/SERVICE_FILE.json")

    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(service_file_path, scopes=scope)
    client_gsheet = gspread.authorize(creds)
    sheet = client_gsheet.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

    # Fetch prompts from Google Sheet
    prompts = sheet.get_all_values()
    print(prompts)  # Debugging

    # Function to generate an image using Stable Diffusion 3.5
    def generate_image(prompt, directory, file, retries=4):
        for attempt in range(1, retries + 1):
            try:
                print(f"🎨 Generating image for: {prompt} (Attempt {attempt})")
                image = client.text_to_image(
                    prompt,
                    model="black-forest-labs/FLUX.1-dev"
                )
                filename = os.path.join(directory, f"{file}.png")
                image.save(filename, format="PNG")  # 🔥 FIX: Convert to PNG format before saving

                print(f"✅ Image saved: {filename}")
                return filename

            except Exception as e:
                print(f"⚠️ Generation failed. Retrying... ({attempt}/{retries})")
                time.sleep(10)  # Wait before retrying

        print(f"❌ Skipping prompt: {prompt} (Image generation failed)")
        return None

    # Get current date for organizing output folders
    current_date = datetime.now().strftime("%d-%m-%Y")

    # Fetch the folder name from the 'topics' sheet
    TOPICS_SHEET = "topics"
    try:
        topics_sheet = client_gsheet.open_by_key(SHEET_ID).worksheet(TOPICS_SHEET)
        topics_data = topics_sheet.get_all_values()
        headers = topics_data[0]
        last_used_index = headers.index("last used")
        genre_index = headers.index("genre")

        folder_name = None
        for row in topics_data[1:]:
            if row[last_used_index].strip().lower() == "this":
                folder_name = row[genre_index].strip()
                break

        folder_name = folder_name if folder_name else "Uncategorized"
    except Exception as e:
        print(f"⚠️ Error accessing Google Sheets: {e}")
        exit(1)

    # Define output directories for GitHub Artifacts
    output_root = os.path.join(os.getcwd(), "workflow_outputs")
    genre_folder = os.path.join(output_root, folder_name)
    date_folder = os.path.join(genre_folder, current_date)
    image_output_dir = os.path.join(date_folder, "image_outputs")

    # Create necessary directories
    os.makedirs(image_output_dir, exist_ok=True)

    # Process all prompts
    for prompt in prompts:
        if len(prompt) < 2:
            print(f"⚠️ Skipping invalid prompt row: {prompt}")
            continue
        generate_image(prompt[1], image_output_dir, prompt[0])

    print("🎉 Image Generation Complete! Images saved in workflow_outputs.")

if __name__ == "__main__":
    image_generation()
