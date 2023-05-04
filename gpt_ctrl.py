import openai
def controller(
    transcript: str,
    system_instruction : str = "You are Sid, the controller for a robotics project. Activate one of these three different control signals as dictionaries upon hearing specific transcription requests:\n\n1. fetching: Activates when asked for your name(Sid) and desk number. Do not activate if a desk number is not specified.\ne.g., transcription: \"Sid, I need you at desk 402\"\n{\n  'action': 'fetch',\n  'desk_destination': '402',\n  'part': 'na',\n  'message': 'na'\n}\n2. request_part: Activates when requesting a part from another desk. Do not activate if a desk number or a part is not specified. \ne.g., transcription: \"Ask lab group 311, for the bosch screwdriver\"\n{\n  'action': 'request_part',\n  'desk_destination': '311',\n  'part': 'bosch screwdriver',\n  'message': 'na'\n}\n3. send_message: Activates when sending a message to another lab group. Do not activate if a desk or a message is not specified.\ne.g., transcription: \"Let desk 304 know that we have finished soldering our h-bridge but the ground is still noisy\"\n{\n  'action': 'send_message',\n  'desk_destination': '304',\n  'part': 'na',\n  'message': 'we are finished soldering our h-bridge, but am having difficulties with a noisy ground'\n}\nOnly activate a control signal if confident the action was requested with all the required parameters. If there is not enough confidence to activate any control signals, then output an empty string\ntranscription: \"",
    model : str = "gpt-4"
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
  message = action_dict.get('message')

  if action == 'fetch':
      announcement = f"Ok. I will head over to desk {desk_destination}."
  elif action == 'request_part':
      announcement = f"Ok. I am going to ask desk {desk_destination} for the {part}."
  elif action == 'send_message':
      announcement = f"Sending message to desk {desk_destination}"
  else:
      announcement = "No action specified."

  return announcement