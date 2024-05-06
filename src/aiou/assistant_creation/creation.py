import json
import os


def create_assistant(client):

    # Print the value of the client object
    print("Client object:", client)

    # Check if the client object is None
    if client is None:
        print("Error: Client object is None.")
        return None

    assets_folder = os.path.join(os.path.dirname(__file__), '..', 'assets')
    assistant_file_path = os.path.join(assets_folder, 'assistant.json')
    knowledge_file_path = os.path.join(assets_folder, 'aiou_format.txt')

    try:
        if os.path.exists(assistant_file_path):
            with open(assistant_file_path, 'r') as file:
                assistant_data = json.load(file)
                assistant_id = assistant_data.get('assistant_id')
                print("Loaded existing assistant ID.")
        else:
            with open(knowledge_file_path, "rb") as knowledge_file:
                file = client.files.create(
                    file=knowledge_file, purpose='assistants')

            assistant = client.beta.assistants.create(
                instructions="""
                   Enter the user by reading the data from the file provided to you and if any user asks you a question other than this file or if you are asked a question other than the data in this file, do not answer it.
                """,
                model="gpt-3.5-turbo-0125",
                tools=[{"type": "file_search"}]
            )

            with open(assistant_file_path, 'w') as file:
                json.dump({'assistant_id': assistant.id}, file)
                print("Created a new assistant and saved the ID.")

            assistant_id = assistant.id

        return assistant_id
    except Exception as e:
        print(f"Error occurred while creating or loading assistant: {e}")
        return None
