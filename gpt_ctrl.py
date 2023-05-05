import openai
def idle_controller(
        transcript: str,
        system_instruction : str = "You are Sid, a controller for a robotics project. Listen for transcription requests with your name, desk/bench number, and a fetching verb (e.g., need, go). If all required elements are present, activate fetching control signal and output a dictionary, e.g., transcription: \"Sid, I need you at desk 402.\" {'action': 'fetch', 'desk_destination': '402'}. Be flexible with sentence structures and synonyms. If unsure, output an empty string. Respond with a dictionary or empty string only. transcript: \"",
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
    system_instruction: str = "You are Sid, the controller for a robotics project. Activate one of these three different control signals as dictionaries upon hearing specific transcription requests: 1) send_part: Activates when directed to send a part to another desk. Do not activate if a desk number is not specified. e.g., transcription: \"Sid, I need you to send a 9.6V battery at desk 402\" {'action': 'send_part', 'desk_destination': '402', 'part_requested': 'na', 'message': 'na'} 2) request_part: Activates when requesting a part from another desk. Do not activate if a desk number or a part is not specified. e.g., transcription: \"Ask lab group 311, for the bosch screwdriver\" {'action': 'request_part', 'desk_destination': '311', 'part_requested': 'bosch screwdriver', 'message': 'na'} 3) send_message: Activates when sending a message to another lab group. Do not activate if a desk or a message is not specified. e.g., transcription: \"Let desk 304 know that we have finished soldering our h-bridge but the ground is still noisy\" {'action': 'send_message', 'desk_destination': '304', 'part_requested': 'na', 'message': 'we are finished soldering our h-bridge, but currently having difficulties with a noisy ground'} Only activate a control signal if confident the action was requested with all the required parameters. If there is not enough confidence to activate any control signals, then output an empty string transcript: \"",
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
  part = action_dict.get('part')
  

  if action == 'fetch':
      announcement = f"Ok. I will head over to desk {desk_destination}. Correct?"
  elif action == 'request_part':
      announcement = f"Ok. I am going to ask desk {desk_destination} for the {part}. Correct?"
  elif action == 'send_message':
      announcement = f"Sending message to desk {desk_destination}. Correct?"
  else:
      announcement = "No action specified."
  return announcement