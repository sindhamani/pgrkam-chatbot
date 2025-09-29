import os
import google.generativeai as genai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- Configuration ---
# To secure your API key, we will use environment variables.
# Create a file named .env in the same directory and add your key like this:
# GEMINI_API_KEY="your_api_key_here"
#GEMINI_API_KEY="AIzaSyAg8wYr1UEesnnn4SP9KZE2aaiqo6m-h4k" - for reference only, to be deleted since it is more secure to load this from the .env hidden file.

from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro-latest')

# --- FastAPI App ---
app = FastAPI()

# This is the crucial security update.
# It tells your backend to only accept requests from your frontend website.
origins = [
    "https://pkgassist.site",
    "http://pkgassist.site",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# This defines the data structure for incoming chat messages
class ChatRequest(BaseModel):
    message: str

# This is the root endpoint for testing
@app.get("/")
def read_root():
    return {"message": "PGRKAM Backend is live!"}

# This is the main endpoint for your chatbot
@app.post("/chat")
async def handle_chat(chat_request: ChatRequest):
    try:
        # Send the user's message to the Gemini model
        response = model.generate_content(chat_request.message)
        
        # Return the model's text response
        return {"reply": response.text}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"reply": "Sorry, I encountered an error."}