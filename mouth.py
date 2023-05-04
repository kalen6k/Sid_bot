import requests
import os
from pydub import AudioSegment
from pydub.playback import play
import io

def play_mp3(mp3_content):
    with io.BytesIO(mp3_content) as file_like_object:
        audio = AudioSegment.from_file(file_like_object, format='mp3')
        play(audio)


CHUNK_SIZE = 1024
url = os.getenv('ELEVENLABS_API_URL')
xi_api_key = os.getenv('ELEVENLABS_API_KEY')
def speak(text: str) -> None:
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
    mp3_content = response.content
    play_mp3(mp3_content)