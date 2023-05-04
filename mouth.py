import requests
import os

CHUNK_SIZE = 1024
url = os.getenv('ELEVENLABS_API_URL')
xi_api_key = os.getenv('ELEVENLABS_API_KEY')
def speak(text: str, transcript_line: int) -> None:
    output_file = f"output_{transcript_line}.mp3"
    headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": xi_api_key
    }

    data = {
    "text": text,
    "voice_settings": {
        "stability": 45,
        "similarity_boost": 90
    }
    }

    response = requests.post(url, json=data, headers=headers)
    with open(output_file, 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)
