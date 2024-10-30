import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import Union, Annotated, List, Dict
from fastapi import FastAPI, File, UploadFile, HTTPException,Body
from fastapi.responses import JSONResponse
 
from pydantic import BaseModel
from datetime import datetime
from data import callapi
# from main import FastAPI
 
# Run with
#  Dev Mode : fastapi dev service_fastapi.py
#  Prod Mode :  fastapi run service_fastapi.py
#       OR
# uvicorn service_arb_router_fastapi:app --host 0.0.0.0 --port 8000
 
# Check docs with
#   http://127.0.0.1:8000/docs
 
description = """
 
## Items
 
You can ** communicate with various chatbots transparently **.
 
## Users
 
You will be able to:
 
* **Check the status of the service** (_implemented_).
* **Get response from various chatbots** (_implemented_).
* **Get upload files for various routes ** (_implemented_).
 
 
"""
 
app = FastAPI(
    title="Demo_DF",
    description=description,
    summary="The service is to route chat messeges to various chatbots",
    version="0.0.1", )
origins = [
        "http://localhost:8080",
        "http://0.0.0.0:8080",
        "https://localhost",
 
 
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
class StatusResponse(BaseModel):
    Status: str
 
    class Config:
        json_schema_extra = {
            "example": {
                "Status": "Running"
            }
        }
 
@app.get("/", response_model=StatusResponse)
def check_status_of_service():
  """
    This endpoint is to just check if the api service is running. <BR>
  """
  return {"Status": "Running"}
 
class Message(BaseModel):
    role: str
    content: str
 
 
# Define a Pydantic model for the response structure
class ResponseModel(BaseModel):
    question: str
 
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Would you like me to help you with something else?",
            }
        }
 
@app.put("/get_llm_response/",  response_model=ResponseModel)
async def get_llm_response(app_cd: str,
                           request_id: str,
                           messages: List[Message]):
  """
  This endpoint is to get the LLM response for a given route. For this you need to provide the needed request parameters along with the msg history in the given format. <BR>
  This end point can be used for 2 purposes <BR>
 
  1) To find the route to which you wish to transfer the request (by sending route_cd as None)<BR>
  2) To get the chat response from the route for a given chat history (by sending the correct route_cd)<BR>
 
  ### The request parameters are
 
  **app_cd** (Not implemented, for future use only): The is the application code to identify which application is sending the request.<BR>
  **request_id** (Not implemented, for future use only): Request id created by the application so that it can be be tracked.<BR>
                            This can be used in future to keep converation histories etc.<BR>
  **messages** (json payload): This is the converation (with history if needed) in the format given in "Request body - Example Value" below.<BR>
 
  Sample :
  <pre>
    [
        {
            "role": "assistant",
            "content": "Hello! Im delighted to assist you with your Resume Assistant"
        },
        {
            "role": "user",
            "content": "List all students who have GenAI skills"
        }
    ]
  </pre>
 
  ### The response structure is as below
 
  **modelreply**: The reply from the large lanbguage model,<BR>
  **status**: Status from the app. (ok/error)<BR>
  **timestamp**: The timestamp of the return response<BR>
 
 
Sample Response:
 
<pre>
    {
        "modelreply": "Would you like me to help you with something else?",
        "status": "ok",
        "timestamp": "2024-09-12T17:41:45.757537"
    }
</pre>
 
  """
  def get_last_user_msg(messages):
      for i in reversed(range(len(messages))):
          if messages[i]['role'] == 'user':
            return messages[i]['content']
      return ""
 
  response_route_conversation=[]
  #print (">>> messages = ", messages)
  messages_json = [{"role": msg.role, "content": msg.content} for msg in messages]
  #print (">>> messages_json = ", messages_json)
  #response_route_conversation = callapi(messages_json)
  chat_last_user_msg = get_last_user_msg(messages_json)
  response_route_conversation = callapi(chat_last_user_msg)
 
  #response_route_conversation = "This is sample response"
  return_payload = {
        "modelreply": response_route_conversation,
        "status": "OK",
        "timestamp" : datetime.now().isoformat()
    }
  print("<<<<<<<<<<<<<<<<<<<<<<<<<<")
  return   JSONResponse(content=return_payload)
