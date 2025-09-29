import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import asyncio
import platform

# --- Configuration & Helper ---
from dotenv import load_dotenv
load_dotenv()

def mask_api_key(api_key):
    if not api_key or len(api_key) <= 4:
        return "Not Set or Invalid"
    return f"...{api_key[-4:]}"

# Global variables
gemini_status = {"status": "unverified", "details": "Checking on startup..."}
api_key_from_env = os.getenv("GEMINI_API_KEY")
masked_key = mask_api_key(api_key_from_env)
MODEL_NAME = "gemini-1.0-pro" # Use the stable, widely available model

# --- Startup Event to Check Gemini ---
async def check_gemini_on_startup():
    global gemini_status
    try:
        if not api_key_from_env:
            raise ValueError("GEMINI_API_KEY not found in .env file.")
        
        genai.configure(api_key=api_key_from_env)
        model = genai.GenerativeModel(MODEL_NAME)
        model.generate_content("test", generation_config={"max_output_tokens": 1})
        
        gemini_status = {"status": "operational", "details": f"Successfully connected to Gemini API using model '{MODEL_NAME}'."}
        print(f"Startup Check: {gemini_status['details']}")
    except Exception as e:
        gemini_status = {"status": "error", "details": str(e)}
        print(f"Startup Check: Failed to connect to Gemini API. Error: {e}")

# --- FastAPI App ---
app = FastAPI(
    title="PGRKAM AI Assistant API",
    version="1.0.0"
)

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

# Define request data structure
class ChatRequest(BaseModel):
    message: str

# --- API Endpoints ---

@app.get("/")
def read_root_and_status():
    """Returns a detailed status of the backend for troubleshooting."""
    return {
        "message": "PGRKAM Backend is live!",
        "backend_status": "active",
        "timestamp_utc": datetime.utcnow().isoformat(),
        "python_version": platform.python_version(),
        "server_info": {
            "model_in_use": MODEL_NAME,
            "gemini_api_key_loaded": masked_key,
            "gemini_api_connection": gemini_status
        }
    }

@app.post("/chat")
async def handle_chat(chat_request: ChatRequest):
    """Handles chat requests and logs them."""
    print(f"INFO: Received message: '{chat_request.message}'")
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(chat_request.message)
        print(f"INFO: Gemini response: '{response.text[:100]}...'")
        return {"reply": response.text}
    except Exception as e:
        print(f"ERROR: An error occurred during chat generation: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while communicating with the AI model.")