from openai import OpenAI
import os
import requests
from dotenv import load_dotenv
from prompts import system_prompt
from actions import get_response_time
from json_helpers import extract_json

# Load environment variables
load_dotenv()

# Create an instance of the OpenAI class
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_text_with_conversation(messages, model="gpt-3.5-turbo"):
    response = openai_client.chat.completions.create(
        model=model,
        messages=messages
    )
    # Access the content of the response
    return response.choices[0].message.content

available_actions = {
    "get_response_time": get_response_time
}

user_prompt = "What is the response time for google.com?"

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt},
]

turn_count = 1
max_turns = 5

while turn_count <= max_turns:
    print(f"Loop: {turn_count}")
    print("----------------------")
    turn_count += 1

    response = generate_text_with_conversation(messages, model="gpt-4")
    print("AI Response:", response)

    json_function = extract_json(response)
    print("Extracted JSON:", json_function)

    if json_function:
        try:
            function_name = json_function[0]['function_name']
            function_params = json_function[0]['function_params']
            if function_name not in available_actions:
                raise Exception(f"Unknown action: {function_name}: {function_params}")
            print(f" -- running {function_name} {function_params}")
            action_function = available_actions[function_name]
            # Call the function
            result = action_function(**function_params)
            function_result_message = f"Action_Response: {result}"
            messages.append({"role": "assistant", "content": function_result_message})
            print(function_result_message)
        except KeyError as e:
            print(f"Key error: {e} in the JSON response: {json_function}")
            break
        except Exception as e:
            print(f"Exception: {e}")
            break
    else:
        print("No valid JSON function found, breaking the loop.")
        break
