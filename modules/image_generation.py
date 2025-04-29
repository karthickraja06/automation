import os
import time
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

def image_generation(sh):
    # Load API Key from .env
    load_dotenv()
    HUGGINGFACE_API_KEY = os.getenv("HF_TOKEN")

    # Initialize Hugging Face Inference Client
    client = InferenceClient(
        provider="hf-inference",
        api_key=HUGGINGFACE_API_KEY
    )
    
    SHEET_NAME = "img_prompt"

    sheet = sh.worksheet(SHEET_NAME)

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
                    model="stabilityai/stable-diffusion-2-1"
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

    # Define output directories for GitHub Artifacts
    output_root = os.path.join(os.getcwd(), "workflow_outputs")
    image_output_dir = os.path.join(output_root, "image_outputs")

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
