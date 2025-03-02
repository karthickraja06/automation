import os
import time
import gspread
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
    service_file_path=os.getenv("SERVICE_FILE_PATH", "secrets/SERVICE_FILE.json")

    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(service_file_path, scopes=scope)
    client_gsheet = gspread.authorize(creds)
    sheet = client_gsheet.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

    # Fetch prompts from Google Sheet
    prompts = sheet.get_all_values()
    print(prompts)  #debugging

    # Create directory for storing images
    os.makedirs("generated_images", exist_ok=True)

    # Function to generate an image using Stable Diffusion 3.5
    def generate_image(prompt,directory,file, retries=4):
        for attempt in range(1, retries + 1):
            try:
                print(f"🎨 Generating image for: {prompt} (Attempt {attempt})")
                image = client.text_to_image(
                    prompt,
                    model="black-forest-labs/FLUX.1-dev"
                )
                filename = os.path.join(directory,f"{file}.png")
                try:
                    with open(filename, "wb") as out:
                        out.write(image)
                    print(f"Generated: {filename}")
                except Exception as e:
                    print(f"Error generating speech for {filename}: {e}")
                

                print(f"✅ Image saved: {filename}")
                return filename

            except Exception as e:
                print(f"⚠️ Generation failed. Retrying... ({attempt}/{retries})")
                time.sleep(10)  # Wait before retrying

        print(f"❌ Skipping prompt: {prompt} (Image generation failed)")
        return None

    current_date = datetime.now().strftime("%d-%m-%Y")

    # Define output directories for GitHub Artifacts
    output_root = os.path.join(os.getcwd(), "workflow_outputs")
    date_folder = os.path.join(output_root, current_date)
    image_output_dir = os.path.join(date_folder, "image_outputs")

    # Create necessary directories
    os.makedirs(image_output_dir, exist_ok=True)

    # Process all prompts
    generated_files = []
    for prompt in prompts:
        image_path = generate_image(prompt[1],image_output_dir,prompt[0])
        if image_path:
            generated_files.append(image_path)

    # Upload to GitHub Artifacts
    if generated_files:
        os.system("gh auth status || gh auth login")
        os.system(f"gh release create v1.0 {' '.join(generated_files)} --title 'Generated Images' --notes 'Auto-generated images'")

        print("✅ Images uploaded to GitHub Artifacts!")
    else:
        print("❌ No images generated.")

    print("🎉 Image Generation Complete!")

if __name__ == "__main__":
    image_generation()