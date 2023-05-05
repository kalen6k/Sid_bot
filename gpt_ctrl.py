import openai
def idle_controller(
        transcript: str,
        system_instruction : str = "You are Sid, a controller for a robotics project. Listen for transcription requests with your name, a 3 digit desk/bench number, and a fetching verb (e.g., need, go). Transcripts are often erroneous, so find plausible 3-digit numbers for desk numbers and account for cases where Sid was transcribed as sit. If all required elements are present, activate fetching control signal and output a dictionary, e.g., transcription: \"Sid, I need you at desk 402.\" {'action': 'fetch', 'desk_destination': '402'}. Be flexible with sentence structures and synonyms. If unsure, output an empty string. Respond with a dictionary or empty string only. transcript \"",
        model: str = "gpt-4",
        ):
    completion = openai.ChatCompletion.create(
        model = model,
        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": transcript + "\""}
        ],
        temperature = 0
    )
    print(completion["choices"][0]["message"]["content"])
    print('', end='', flush=True)
    return completion["choices"][0]["message"]["content"]
                        
def fetched_controller(
    transcript: str,
    system_instruction: str = "You are Sid, the controller for a robotics project. Activate a control signal as a dictionary upon request for a part delivery.\n send_part: Activates when directed to send a part to another desk. Do not activate if a desk number is not specified. e.g., transcription: \"Sid, I need you to send a 9.6V battery at desk 402\" {'action': 'send_part', 'desk_destination': '402'} Only activate a control signal if confident the action was requested with a 3-digit desk/bench destination. Transcripts are often erroneous, so find plausible 3-digit numbers for desks and account for cases where Sid was transcribed as sit. If there is not enough confidence to activate the  control signal, then output an empty string.\n transcript: \"",
    model: str = "gpt-4"
    ):
  completion = openai.ChatCompletion.create(
      model = model,
      messages = [
          {"role": "system", "content": system_instruction},
          {"role": "user", "content": transcript + "\""}
      ], 
      temperature = 0
    )
  print(completion["choices"][0]["message"]["content"])
  print('', end='', flush=True)
  return completion["choices"][0]["message"]["content"]

def announce_action(action_dict):
  action = action_dict.get('action')
  desk_destination = action_dict.get('desk_destination')
  
  

  if action == 'fetch':
      announcement = f"Ok. I will head over to desk {desk_destination}."
  elif action == 'send_part':
      announcement = f"Ok. I will take it to desk {desk_destination}."
  else:
      announcement = "I am sorry, I did not catch that."
  return announcement
