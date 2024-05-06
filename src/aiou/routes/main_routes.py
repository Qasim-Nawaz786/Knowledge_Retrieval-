import json
import asyncio

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel

from src.aiou.database.database_connectivity import OPENAI_API_KEY,  create_db_engine
from src.aiou.assistant_creation.creation import create_assistant
from src.aiou.models.pydantic_models import ChatRequest, ChatResponse, api_call_arguments

from ..openai.openai_connectivity import version_check, create_client

version_check()

#### this commented part will be used when function_calling will be implemented with assistant
# Database setup
# Ensure database_url is not None before passing it to create_engine
# engine = create_db_engine()

# # function for creating the QueryLog in database if not created
# def create_db_and_tables():
#     SQLModel.metadata.create_all(engine)

# # @asynccontextmanager / create_db_and_tables
# def lifespan(app: FastAPI):
#     create_db_and_tables()

def show_json(message, obj):
    print(message, json.loads(obj.model_dump_json()))

app = FastAPI()

# Init OpenAI client bys self made function
client = create_client(OPENAI_API_KEY)

# Create new assistant or load existing
assistant_id = create_assistant(client)

# start the conversation by creating a new assistant thread id
@app.get('/start')
async def start_conversation():
    thread = client.beta.threads.create()
    thread_id = thread.id
    print({"thread_id": thread_id})
    return {"thread_id": thread_id}

#  creation which will communicate with database incorporated within fastapi endpoints

@app.get('/') 
def hello_world():
    return {"message": "This is aiou's assistant backend!"}


# start the conversation using assistant via ('/chat') api endpoint
@app.post('/chat')
async def chat(request: ChatRequest):
    thread_id:str = request.thread_id
    user_input: str = request.message
    
    if not thread_id:
        print("Error: Missing thread id")
        return JSONResponse({"Error": "Missing thread id"}), 400

    print(f"recieved message: {user_input} for thread: {thread_id}")

    #adding user message to the thread
    client.beta.threads.messages.create(thread_id=thread_id, role="user", content=user_input)

    # #running the assistant
    run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id= assistant_id)

    # check run_status
    while True:
        run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        print(f"Run status: {run_status.status}")
        if run_status.status == 'completed':
            break
        await asyncio.sleep(1)
        
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    
    #parsing the messages
    if messages.data[0].content:
        message_content = messages.data[0].content[0]
        if hasattr(message_content, 'text'):
            response = message_content.text.value
            print(response)
        elif hasattr(message_content, 'image_file'):
            #To Handle the case where it's an image file
            print("Received an image message.")
        else:
            # Fallback for unrecognized types
            print("Received an unrecognized type of message.")
        return JSONResponse({"response": response})
    else:
        print("The latest message has no content.")
        return JSONResponse({"Error": "The latest message has no content"}, status_code=404)
    

############ this commented part will also be used when function_calling is implemented

# from typing import Optional, Dict, Any
# import httpx

# async def make_internal_api_call(function_name: str, arguments: Optional[Dict[str, Any]] = None):
#     try:
#         async with httpx.AsyncClient() as client:
#             base_url = "http://localhost:8000"

#             if function_name == "get_person_location":
#                 if arguments and "name" in arguments:
#                     url = f"{base_url}/location/{arguments['name']}"
#                     response = await client.get(url)
#                 else:
#                     return {"error": "Missing required 'name' argument for 'get_person_location'"}

#             elif function_name == "read_all_persons":
#                 url = f"{base_url}/persons/"
#                 response = await client.get(url)

#             elif function_name == "create_person":
#                 if arguments and "name" in arguments and "location" in arguments:
#                     url = f"{base_url}/person/"
#                     # Passing the dictionary directly as JSON
#                     response = await client.post(url, json={"name": arguments["name"], "location": arguments["location"]})
#                 else:
#                     return {"error": "Missing required arguments for 'create_person'"}

#             else:
#                 return {"error": "Unsupported action"}

#             try:
#                 return response.json()
#             except ValueError:  # Includes simplejson.errors.JSONDecodeError
#                 return {"error": "Failed to decode JSON response"}
#     except httpx.ReadTimeout:
#         # Handle the ReadTimeout exception here
#         return {"error": "ReadTimeout occurred while making the internal API call"}