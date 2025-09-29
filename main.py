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

# --- NEW: GCP Project Configuration ---
PROJECT_ID = "poetic-bison-473505-v7"  # Your GCP Project ID
LOCATION = "asia-south1"            # Your server's region (Mumbai)

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)

MODEL_NAME = "gemini-1.0-pro"

# --- FastAPI App ---
app = FastAPI(title="PGRKAM AI Assistant API")

# (CORS Middleware and BaseModel remain the same as before)
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
    # (This endpoint remains the same as before)
    return {
        "message": "PGRKAM Backend is live!",
        "backend_status": "active",
        "timestamp_utc": datetime.utcnow().isoformat(),
        "python_version": platform.python_version(),
        "server_info": {
            "gcp_project_id": PROJECT_ID,
            "gcp_location": LOCATION,
            "model_in_use": MODEL_NAME,
        }
    }

@app.post("/chat")
async def handle_chat(chat_request: ChatRequest):
    print(f"INFO: Received message: '{chat_request.message}'")
    try:
        # --- NEW: Updated way to call the model ---
        model = GenerativeModel(MODEL_NAME)
        response = model.generate_content(chat_request.message)

        print(f"INFO: Gemini response: '{response.text[:100]}...'")
        return {"reply": response.text}
    except Exception as e:
        print(f"ERROR: An error occurred during chat generation: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while communicating with the AI model.")