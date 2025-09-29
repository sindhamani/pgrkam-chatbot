import os
import google.generativeai as genai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import asyncio

# --- Configuration ---
from dotenv import load_dotenv
load_dotenv()

# --- Helper Function ---
def mask_api_key(api_key):
    """Masks the API key, showing only the last 4 characters."""
    if not api_key or len(api_key) <= 4:
        return "Invalid or too short"
    return f"...{api_key[-4:]}"

# Global variable to hold Gemini status
gemini_status = {"status": "unverified", "details": "Checking on startup..."}
api_key_from_env = os.getenv("GEMINI_API_KEY")
masked_key = mask_api_key(api_key_from_env)

# --- Startup Event ---
async def check_gemini_on_startup():
    """Checks Gemini API connectivity when the application starts."""
    global gemini_status
    try:
        if not api_key_from_env:
            raise ValueError("GEMINI_API_KEY not found in environment.")
            
        genai.configure(api_key=api_key_from_env)
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        model.generate_content("test", generation_config={"max_output_tokens": 1})
        
        gemini_status = {"status": "operational", "details": "Successfully connected to Gemini API."}
        print("Startup Check: Gemini API connection successful.")
    except Exception as e:
        gemini_status = {"status": "error", "details": str(e)}
        print(f"Startup Check: Failed to connect to Gemini API. Error: {e}")

# --- FastAPI App ---
app = FastAPI(title="PGRKAM AI Assistant API")

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(check_gemini_on_startup())

# Configure CORS
origins = ["https://pkgassist.site", "http://pkgassist.site"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the request data structure
class ChatRequest(BaseModel):
    message: str

# --- API Endpoints ---

@app.get("/")
def read_root():
    """Returns the backend's root message."""
    return {"message": "PGRKAM Backend is live! Visit /status for detailed health check."}

@app.get("/status")
def get_status():
    """Returns a detailed status of the backend and its connection to Gemini."""
    return {
        "backend_status": "active",
        "timestamp": datetime.now().isoformat(),
        "gemini_api_key_loaded": masked_key,
        "gemini_api_connection": gemini_status
    }

@app.post("/chat")
async def handle_chat(chat_request: ChatRequest):
    """Handles chat requests by sending them to the Gemini API."""
    print(f"Received message: '{chat_request.message}'")
    try:
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        response = model.generate_content(chat_request.message)
        print(f"Gemini response: '{response.text[:100]}...'")
        return {"reply": response.text}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"reply": "Sorry, I encountered an error."}