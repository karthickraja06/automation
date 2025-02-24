import os
import gspread
from google.oauth2.service_account import Credentials
from google.cloud import texttospeech
from dotenv import load_dotenv
import shutil


def generate_speech():
    # Load environment variables
    load_dotenv()

    # Define API Scopes
    SHEETS_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    TTS_SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

    # Get service file paths from environment variables
    service_file_path = os.getenv("SERVICE_FILE_PATH", "secrets/SERVICE_FILE.json")  # This now contains the actual file path
    tts_service_file_path = os.getenv("TTS_SERVICE_FILE_PATH", "secrets/TTS_SERVICE_FILE.json")

    if not service_file_path or not os.path.exists(service_file_path):
        raise ValueError("Missing or invalid SERVICE_FILE_PATH")

    if not tts_service_file_path or not os.path.exists(tts_service_file_path):
        raise ValueError("Missing or invalid TTS_SERVICE_FILE_PATH")

    # Authenticate Google Sheets
    sheets_creds = Credentials.from_service_account_file(service_file_path, scopes=SHEETS_SCOPES)
    sheets_client = gspread.authorize(sheets_creds)

    # Authenticate Google Text-to-Speech
    tts_creds = Credentials.from_service_account_file(tts_service_file_path, scopes=TTS_SCOPES)
    tts_client = texttospeech.TextToSpeechClient(credentials=tts_creds)


    # Load Google Sheet
    SHEET_ID = os.getenv("SHEET_ID")
    SHEET_NAME = "response"

    try:
        sheet = sheets_client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
        rows = sheet.get_all_values()[1:]  # Fetch all values (excluding headers)
    except Exception as e:
        print(f"Error accessing Google Sheets: {e}")
        exit(1)

    # Function to Generate Audio
    def generate_speech(text, gender, filename):
        voice_params = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Wavenet-D" if gender.lower() == "male" else "en-US-Wavenet-F"
        )
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

        # SSML for better voice modulation
        ssml_text = f"<speak>{text}</speak>"
        synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)

        try:
            response = tts_client.synthesize_speech(input=synthesis_input, voice=voice_params, audio_config=audio_config)
            with open(filename, "wb") as out:
                out.write(response.audio_content)
            print(f"Generated: {filename}")
        except Exception as e:
            print(f"Error generating speech for {filename}: {e}")

    output_dir = "audio_outputs"

    # Delete the folder and recreate it
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)  # Deletes the entire folder and its contents

    os.makedirs(output_dir, exist_ok=True)  # Recreate the folder

    # Process Each Dialogue
    for index, (name, gender, dialogue) in enumerate(rows, start=1):
        filename = os.path.join(output_dir, f"{index:02d}_{name}.mp3")
        generate_speech(dialogue, gender, filename)

    print("All dialogues converted to speech successfully!")


if __name__ == "__main__":
    generate_speech()
    print("Script completed.")