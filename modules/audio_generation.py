import os
from google.oauth2.service_account import Credentials
from google.cloud import texttospeech
from dotenv import load_dotenv
from datetime import datetime

def audio_generation(sheet):
    # Load environment variables
    load_dotenv()

    # Define API Scopes
    TTS_SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

    # Get service file paths from environment variables
    tts_service_file_path = os.getenv("TTS_SERVICE_FILE_PATH", "secrets/TTS_SERVICE_FILE.json")

    # Authenticate Google Text-to-Speech
    tts_creds = Credentials.from_service_account_file(tts_service_file_path, scopes=TTS_SCOPES)
    tts_client = texttospeech.TextToSpeechClient(credentials=tts_creds)

    # Load Sheets
    RESPONSE_SHEET = "response"
    TOPICS_SHEET = "topics"

    try:
        response_sheet = sheet.worksheet(RESPONSE_SHEET)
        topics_sheet = sheet.worksheet(TOPICS_SHEET)

        rows = response_sheet.get_all_values()[1:]  # Fetch all values excluding headers

        # Find the folder name from 'topics' sheet
        topics_data = topics_sheet.get_all_values()
        headers = topics_data[0]
        last_used_index = headers.index("last used")
        genre_index = headers.index("genre")

        folder_name = None
        for row in topics_data[1:]:
            if row[last_used_index].strip().lower() == "this":
                folder_name = row[genre_index].strip()
                break

        # Default folder name if no match is found
        if not folder_name:
            folder_name = "Uncategorized"

    except Exception as e:
        print(f"Error accessing Google Sheets: {e}")
        exit(1)

    # Get the current date (DD-MM-YYYY format)
    current_date = datetime.now().strftime("%d-%m-%Y")

    # Define output directories for GitHub Artifacts
    output_root = os.path.join(os.getcwd(), "workflow_outputs")
    genre_folder = os.path.join(output_root, folder_name)
    date_folder = os.path.join(genre_folder, current_date)
    audio_output_dir = os.path.join(date_folder, "audio_outputs")

    # Create necessary directories
    os.makedirs(audio_output_dir, exist_ok=True)

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

    # Process Each Dialogue
    for index, (name, gender, dialogue) in enumerate(rows, start=1):
        filename = os.path.join(audio_output_dir, f"{index:02d}_{name}.mp3")
        generate_speech(dialogue, gender, filename)

    print("Step 4 - All dialogues converted to speech successfully!")

if __name__ == "__main__":
    audio_generation()
    print("Script completed.")
