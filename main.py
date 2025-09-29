import os
import vertexai
from vertexai.generative_models import GenerativeModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import platform

# --- Configuration ---
from dotenv import load_dotenv
load_dotenv()

# --- GCP Project Configuration ---
# This explicitly tells the library which project and location to use.
PROJECT_ID = "poetic-bison-473505-v7"
LOCATION = "asia-south1"

# Initialize Vertex AI with explicit credentials
# This is the key fix to ensure it authenticates correctly on the VM.
vertexai.init(project=PROJECT_ID, location=LOCATION)

MODEL_NAME = "gemini-1.0-pro"

# --- FastAPI App ---
app = FastAPI(title="PGRKAM AI Assistant API")

# (CORS Middleware and BaseModel remain the same)
origins = ["https://pkgassist.site", "http://pkgassist.site"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class ChatRequest(BaseModel):
    message: str

# --- API Endpoints ---
@app.get("/")
def read_root_and_status():
    return {"message": "PGRKAM Backend is live!"}

@app.post("/chat")
async def handle_chat(chat_request: ChatRequest):
    print(f"INFO: Received message: '{chat_request.message}'")
    try:
        model = GenerativeModel(MODEL_NAME)
        response = model.generate_content(chat_request.message)

        print(f"INFO: Gemini response: '{response.text[:100]}...'")
        return {"reply": response.text}
    except Exception as e:
        print(f"ERROR: An error occurred during chat generation: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")