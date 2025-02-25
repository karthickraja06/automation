import os
import gspread
import google.generativeai as genai
import json
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

def image_prompt_generation(input_script):
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
    try:
        script_json = json.loads(response.text)  # Convert response to JSON
        return script_json
    except (json.JSONDecodeError, AttributeError) as e:
        print("Error parsing JSON:", str(e))
        return None
    finally:
        del model  # Delete model instance

def image_generation(json_data):
    if not isinstance(json_data, dict):
        raise ValueError("Invalid input JSON. Expected a dictionary.")

    input_script = json.dumps(json_data) + """
    Generate the response in only JSON output like:
    ```json
    {1: "prompt1", 2: "prompt2", ..., "nth": "prompt nth"}
    ```
    Strictly no other output should be in the response. Only and only the prompts as a JSON response.
    Provide me with at least 4 text prompts to generate images related to the script.
    The pictures should be super vivid, colorful, 3D, and hyper-realistic.
    """

    response = image_prompt_generation(input_script)

    if not response or not isinstance(response, dict):
        print("Invalid response from AI")
        return

    SPREADSHEET_ID = os.getenv("SHEET_ID")
    SHEET4_NAME = "img_prompt"

    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    service_file_path = os.getenv("SERVICE_FILE_PATH", "secrets/SERVICE_FILE.json")

    if not service_file_path or not os.path.exists(service_file_path):
        raise ValueError("Missing or invalid SERVICE_FILE_PATH")

    creds = Credentials.from_service_account_file(service_file_path, scopes=SCOPES)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SPREADSHEET_ID)
    sheet4 = sh.worksheet(SHEET4_NAME)

    # Ensure response is a dictionary and append data properly
    for key, val in response.items():
        sheet4.append_row([key, val])  # Append key-value pair for better readability

    print("Google Sheets updated successfully!")
