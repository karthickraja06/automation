import os
import time
import requests
from dotenv import load_dotenv
from datetime import datetime

def image_generation(sh):
    # Load environment variables
    load_dotenv()
    
    # Get API token
    HF_TOKEN = os.getenv("HF_TOKEN")
    if not HF_TOKEN:
        raise ValueError("HF_TOKEN not found in environment variables")

    # API configuration
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }

    def generate_image(prompt, output_path, index):
        """Generate a single image from a prompt"""
        try:
            print(f"🎨 Generating image {index}: {prompt}")
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "width": 1024,
                    "height": 1024,
                    "num_inference_steps": 50,
                    "guidance_scale": 7.5
                }
            }

            # Make API request
            response = requests.post(API_URL, headers=headers, json=payload)
            response.raise_for_status()

            # Save the image
            image_path = os.path.join(output_path, f"image_{index:02d}.png")
            with open(image_path, "wb") as f:
                f.write(response.content)
            
            print(f"✅ Saved image: {image_path}")
            return image_path

        except Exception as e:
            print(f"❌ Error generating image {index}: {str(e)}")
            return None

    try:
        # Get prompts from sheet
        worksheet = sh.worksheet("img_prompt")
        rows = worksheet.get_all_values()[1:]  # Skip header row
        
        # Setup output directory
        current_date = datetime.now().strftime("%d-%m-%Y")
        output_dir = os.path.join(os.getcwd(), "workflow_outputs", "image_outputs", current_date)
        os.makedirs(output_dir, exist_ok=True)

        # Generate images
        generated_files = []
        for i, row in enumerate(rows, 1):
            if len(row) < 2:  # Skip invalid rows
                continue
                
            prompt = row[1]
            # Add retry logic
            for attempt in range(3):
                result = generate_image(prompt, output_dir, i)
                if result:
                    generated_files.append(result)
                    break
                print(f"Retrying... (Attempt {attempt + 1}/3)")
                time.sleep(5)

        print(f"🎉 Generated {len(generated_files)} images")
        return generated_files

    except Exception as e:
        print(f"❌ Error in image generation process: {str(e)}")
        return []

if __name__ == "__main__":
    # For testing the module directly
    from google.oauth2.service_account import Credentials
    import gspread
    
    load_dotenv()
    SHEET_ID = os.getenv("SHEET_ID")
    service_file_path = os.getenv("SERVICE_FILE")
    
    creds = Credentials.from_service_account_file(
        service_file_path, 
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SHEET_ID)
    
    image_generation(sh)
