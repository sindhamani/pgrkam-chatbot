import os
import google.generativeai as genai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- Configuration ---
# To secure your API key, we will use environment variables.
# Create a file named .env in the same directory and add your key like this:
# GEMINI_API_KEY="your_api_key_here"
from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro-latest')

# --- FastAPI App ---
app = FastAPI()

# Allow connections from your Hostinger frontend
origins = ["*"]  # For development, "*" is okay. For production, specify your domain.
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

@app.get("/")
def read_root():
    return {"message": "Hello from Bengaluru! The PGRKAM Backend is running!"}

@app.post("/chat")
async def handle_chat(chat_request: ChatRequest):
    try:
        # Send the user's message to the Gemini model
        response = model.generate_content(chat_request.message)

        # Return the model's response
        return {"reply": response.text}
    except Exception as e:
        return {"reply": f"An error occurred: {e}"}