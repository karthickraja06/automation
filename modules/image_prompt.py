import os
import gspread
import google.generativeai as genai
import json
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import grpc

load_dotenv()

def shutdown_grpc():
    try:
        grpc._channel._Rendezvous.__del__ = lambda self: None  # Suppress errors
    except AttributeError:
        pass

def image_prompt_generation(input_script):
    """Generates image prompts using Gemini AI."""
    GEMINI_API_KEY = os.getenv("GEMINI_API")
    if not GEMINI_API_KEY:
        raise ValueError("Missing Gemini API Key. Set GEMINI_API_KEY in environment variables.")

    genai.configure(api_key=GEMINI_API_KEY)

    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "application/json",  # Expecting JSON response
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )

    response = model.generate_content(input_script)

    # Ensure response is correctly parsed as JSON
    shutdown_grpc()
    try:
        script_json = json.loads(response.text)  # Convert response to JSON
        print(script_json)
        return script_json
    except (json.JSONDecodeError, AttributeError) as e:
        print("Error parsing JSON:", str(e))
        return None
    finally:
        del model  # Delete model instance

def image_prompt_organize(sh):
    """Fetches script from Sheet3, generates image prompts, and stores them in Sheet4."""
    sheet3 = sh.worksheet("img_prompt")  # Access 'script' sheet
    sheet3_data = sheet3.get_all_values()  # Fetch data from 'response' sheet

    # Convert sheet data (list of lists) into a single script string
    script_text = "\n".join([" # ".join(row) for row in sheet3_data if any(row)])  # Join non-empty rows

    input_script = script_text + """
    Generate the response in only JSON output like:
    ```json
    {1: "prompt1", 2: "prompt2", ..., "nth": "prompt nth"}
    ```
    Strictly no other output should be in the response. Only and only the prompts as a JSON response.
    Provide me one image prompt for each scene between # 
    if scene(are the one between #) are less that 4 give me at least 4 text prompts to generate images related to the script.
    The pictures should be super vivid, colorful, 3D, and hyper-realistic.
    """

    response = image_prompt_generation(input_script)

    if not response or not isinstance(response, dict):
        print("Invalid response from AI")
        return

    sheet4 = sh.worksheet("img_prompt")

    sheet4.clear()  # Clear existing data in Sheet4

    # Store AI-generated prompts in Sheet4
    for key, val in response.items():
        # Ensure `val` is converted to a string and not a list
        if isinstance(val, list):  
            val = " | ".join(val)  # Join list items into a single string

        sheet4.append_row([key, val])  # Append key-value pair

    print("Step 5 - Google Sheets updated successfully!")

if __name__ == "__main__":
    image_prompt_organize()
    print(" Step 5 - prompt complete completed.")