import io
import os
import speech_recognition as sr
import openai
import wave

from datetime import datetime, timedelta
from queue import Queue
from tempfile import NamedTemporaryFile
from time import sleep
from gpt_ctrl import idle_controller, fetched_controller, announce_action
from smart_mouth import speak
import ast

# Robot states
IDLE = 0
FETCH = 1
DELIVERING_PART = 2
REQUEST_1 = 3
REQUEST_2 = 4
DELIVERING_MESSAGE = 5

def ear(state, energy_threshold: int = 1800, record_timeout: float = 2, phrase_timeout: float = 1.2):
    # this works if your default microphone is set correctly
    source = sr.Microphone(sample_rate=16000)
    # The last time a recording was retreived from the queue.
    phrase_time = None
    # Current raw audio bytes.
    last_sample = bytes()
    # Thread safe Queue for passing data from the threaded recording callback.
    data_queue = Queue()
    # We use SpeechRecognizer to record our audio because it has a nice feauture where it can detect when speech ends.
    recorder = sr.Recognizer()
    recorder.energy_threshold = energy_threshold
    # Definitely do this, dynamic energy compensation lowers the energy threshold dramtically to a point where the SpeechRecognizer never stops recording.
    recorder.dynamic_energy_threshold = False

    temp_file = NamedTemporaryFile(suffix='.wav', delete = False).name
    transcription = ['']
    transcription_line = 0
    action_dict = []
    action_recieved = False
    with source as temp_source:
        recorder.adjust_for_ambient_noise(temp_source)
        
    def record_callback(_, audio:sr.AudioData) -> None:
        """
        Threaded callback function to recieve audio data when recordings finish.
        audio: An AudioData containing the recorded bytes.
        """
        # Grab the raw bytes and push it into the thread safe queue.
        try:
            data = audio.get_raw_data()
            data_queue.put(data)
        except Exception as e:
            print(f"Error in record_callback: {e}")
    
    def whisperAPI(filename):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        audio_file = open(filename, "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        return transcript
    
    
    
    recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)
    start_time = datetime.utcnow()
    
    while True:
        try:
            now = datetime.utcnow()
            # Pull raw recorded audio from the queue.
            if not data_queue.empty():
                phrase_complete = False
                # If enough time has passed between recordings, consider the phrase complete.
                # Clear the current working audio buffer to start over with the new data.
                if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                    last_sample = bytes()
                    phrase_complete = True
                # This is the last time we received new audio data from the queue.
                phrase_time = now

                # Concatenate our current audio data with the latest audio data.
                while not data_queue.empty():
                    data = data_queue.get()
                    last_sample += data

                # Use AudioData to convert the raw data to wav data.
                audio_data = sr.AudioData(last_sample, source.SAMPLE_RATE, source.SAMPLE_WIDTH)
                wav_data = io.BytesIO(audio_data.get_wav_data())
                
                    
                # Write wav data to a wav file for api request
                with wave.open(temp_file, 'wb') as f:
                    f.setnchannels(1)
                    f.setsampwidth(2)
                    f.setframerate(16000)
                    f.writeframes(wav_data.read())
                
                if now - start_time > timedelta(seconds=1):
                    # Read the transcription.
                    result = whisperAPI(temp_file)
                    text = result['text'].strip()

                    # If we detected a pause between recordings, add a new item to our transcripion.
                    # Otherwise edit the existing one.
                    if phrase_complete:
                        transcription.append(text)
                        transcription_line+=1
                    else:
                        transcription[-1] = text

                    if not action_recieved:
                        # remove the text before the occurence of "Sid" in the transcription
                        # this is to only process the text once the user says "Sid"
                        text = transcription[transcription_line]
                        sit_index = text.find("Sit")
                        sid_index = text.find("Sid")
                        index = 0
                        if sid_index != -1 or sit_index != -1:
                            if sid_index == -1:
                                index = sit_index
                            else:
                                index = sid_index
                            speak("hmmmmmmm")
                            text = text[index:]
                            if state == IDLE:
                                print("in idle ctrl")
                                print(text)
                                action_str = idle_controller(text)
                                try:
                                    print("try")
                                    if action_str == "":
                                        raise Exception
                                    action_dict = ast.literal_eval(action_str)
                                    print("action_confirmed")
                                    action_recieved = True
                                    speak(announce_action(action_dict))
                                    return action_dict
                                except:
                                    action_recieved = False
                                    print("except")
                                    action_dict = []
                            elif state == FETCH:
                                print("in fetch ctrl")
                                print(text)
                                action_str = fetched_controller(text)
                                try:
                                    action_dict = ast.literal_eval(action_str)
                                    print("action_confirmed")
                                    action_recieved = True
                                    speak(announce_action(action_dict))
                                    return action_dict
                                except:
                                    action_recieved = False
                                    print("except")
                                    action_dict = []
                    # Clear the console to reprint the updated transcription.
                    #os.system('cls' if os.name=='nt' else 'clear')
                    print(transcription[transcription_line])
                    # Flush stdout.
                    print('', end='', flush=True)

                # Infinite loops are bad for processors, must sleep.
                sleep(0.25)
        except KeyboardInterrupt:
            break

    print("\n\nTranscription:")
    for line in transcription:
        print(line)
        print('\n')


if __name__ == "__main__":
    state = IDLE
    ear(state)
