import os
import google.generativeai as genai
import json
from dotenv import load_dotenv
from modules.prompt import sync_google_sheets_data  # Import the function

def script_generation():
    
    load_dotenv()
    # Load Gemini AI API Key from environment variables
    GEMINI_API_KEY = os.getenv("GEMINI_API")

    if not GEMINI_API_KEY:
        raise ValueError("Missing Gemini API Key. Set GEMINI_API_KEY in environment variables.")

    # Configure the API
    genai.configure(api_key=GEMINI_API_KEY)

    # Define model configuration
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "application/json",  # Expecting JSON response
    }

    # Create the model instance
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )

    # Generate the script instruction
    script_prompt = sync_google_sheets_data()  # Call function from prompt.py
    response = model.generate_content(script_prompt)

    # Parse JSON response
    try:
        script_json = json.loads(response.text)  # Convert response to JSON
        return(script_json)  # Print JSON output
    except json.JSONDecodeError as e:
        print("Error parsing JSON:", str(e))
        script_json = None  # Handle parsing error
    del model # Delete model instance
    

# Next step: Use `script_json` for further processing (e.g., image generation)
if __name__ == "__main__":
    script_json = script_generation()
    if script_json:
        print(script_json)
        print("Script generation completed.")
    else:
        print("Script generation failed.")
    print("Script generation completed.")
