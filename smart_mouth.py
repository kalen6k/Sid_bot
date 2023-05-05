from elevenlabs import generate, play, set_api_key
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv('ELEVENLABS_API_KEY')
set_api_key(api_key)
from elevenlabs import Voices
def list_voices():
    voices = Voices.from_api()
    for voice in voices:
        print(voice.name)
def speak(text: str):
    audio = generate(
        text=text,
        voice="5Peczo01i4r960jexOus",
    )
    play(audio)

if __name__ == "__main__":
    speak("Hello world! Why are you waking me up at 2:17 bitch?")