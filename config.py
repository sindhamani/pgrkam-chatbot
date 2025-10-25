# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the PGRKAM Digital Assistant"""

    # --- API Keys ---
    # !! REMOVED DEFAULT KEY - Load ONLY from .env file !!
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '') # Default to empty string if not in .env
    # GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '') # Not needed for VM auth

    # --- GCP Settings ---
    PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT', 'poetic-bison-473505-v7')
    # --- Corrected LOCATION (Region only) ---
    LOCATION = os.getenv('GOOGLE_CLOUD_LOCATION', 'asia-south1') # Use region, not zone

    # --- Database (SQLite focus) ---
    SQLITE_DB_PATH = os.getenv('SQLITE_DB_PATH', 'chatbot.db')
    # Cloud SQL Connection (Leave empty if not using)
    CLOUD_SQL_CONNECTION_NAME = os.getenv('CLOUD_SQL_CONNECTION_NAME', '')
    DB_USER = os.getenv('DB_USER', '')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', '')

    # --- Application Settings ---
    APP_NAME = os.getenv('APP_NAME', 'PGRKAM Digital Assistant')
    APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true' # Default DEBUG to False

    # --- Language Settings ---
    DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE', 'en')
    # SUPPORTED_LANGUAGES = os.getenv('SUPPORTED_LANGUAGES', 'en,hi,pa').split(',') # Keep if using env var
    SUPPORTED_LANGUAGES = ['en', 'hi', 'pa'] # Or define directly

    # --- Gemini Model Settings ---
    # Use the model that worked or you intend to test
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash-latest')
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '1024')) # Reduced default slightly
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))

    # --- Settings below are currently unused by the streamlined gemini_chatbot.py ---
    # Audio Settings (Can be kept or removed if voice features are not planned)
    # SPEECH_RATE = int(os.getenv('SPEECH_RATE', '150'))
    # SPEECH_VOLUME = float(os.getenv('SPEECH_VOLUME', '0.8'))
    # VOICE_GENDER = os.getenv('VOICE_GENDER', 'male')

    # RAG Settings (Can be kept or removed if RAG is not implemented yet)
    # CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '1000'))
    # CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '200'))
    # TOP_K_RESULTS = int(os.getenv('TOP_K_RESULTS', '3'))
    # USE_VERTEX_AI_FOR_RAG = os.getenv('USE_VERTEX_AI_FOR_RAG', 'False').lower() == 'true' # Renamed for clarity

    # Job Recommendation Settings (Can be kept or removed)
    # MAX_JOB_RECOMMENDATIONS = int(os.getenv('MAX_JOB_RECOMMENDATIONS', '5'))

    # Language mappings (Useful metadata)
    LANGUAGE_NAMES = {'en': 'English', 'hi': 'Hindi', 'pa': 'Punjabi'}

    # Categories/Skills (Useful metadata)
    JOB_CATEGORIES = [
        'Government Jobs', 'Private Sector', 'Skill Development', 'Foreign Counseling',
        'Education', 'Healthcare', 'Technology', 'Agriculture', 'Banking', 'Defense'
    ]
    SKILL_AREAS = [
        'Digital Literacy', 'Communication Skills', 'Technical Skills', 'Language Learning',
        'Leadership', 'Entrepreneurship', 'Computer Skills', 'Soft Skills'
    ]
# import os
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# class Config:
#     """Configuration class for the PGRKAM Digital Assistant"""
    
#     # API Keys
#     GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
#     #GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
    
#     # Vector Store Configuration (using Google Cloud alternatives)
#     USE_VERTEX_AI = os.getenv('USE_VERTEX_AI', 'False').lower() == 'true'
#     PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT', 'poetic-bison-473505-v7')
#     LOCATION = os.getenv('GOOGLE_CLOUD_LOCATION', 'asia-south1-b')
    
#     # Database Configuration
#     DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///chatbot.db')
    
#     # Application Settings
#     APP_NAME = os.getenv('APP_NAME', 'PGRKAM Digital Assistant')
#     APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
#     DEBUG = os.getenv('DEBUG', 'False').lower() == 'true' # Default DEBUG to False for production       
#     # Language Settings
#     DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE', 'en')
#     SUPPORTED_LANGUAGES = os.getenv('SUPPORTED_LANGUAGES', 'en,hi,pa').split(',')
    
#     # Audio Settings
#     SPEECH_RATE = int(os.getenv('SPEECH_RATE', '150'))
#     SPEECH_VOLUME = float(os.getenv('SPEECH_VOLUME', '0.8'))
#     VOICE_GENDER = os.getenv('VOICE_GENDER', 'male')
    
#     # RAG Settings
#     CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '1000'))
#     CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '200'))
#     TOP_K_RESULTS = int(os.getenv('TOP_K_RESULTS', '3'))
    
#     # Gemini Model Settings
#     GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash-latest')
#     MAX_TOKENS = int(os.getenv('MAX_TOKENS', '2048'))
#     TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))
    
#     SQLITE_DB_PATH = os.getenv('SQLITE_DB_PATH', 'chatbot.db') # Explicitly define DB path
#     # Google Cloud Settings
#     CLOUD_SQL_CONNECTION_NAME = os.getenv('CLOUD_SQL_CONNECTION_NAME', '') # e.g., "your-project:your-region:your-instance"
#     DB_USER = os.getenv('DB_USER', '')
#     DB_PASSWORD = os.getenv('DB_PASSWORD', '')
#     DB_NAME = os.getenv('DB_NAME', '')
    
#     # Job Recommendation Settings
#     MAX_JOB_RECOMMENDATIONS = int(os.getenv('MAX_JOB_RECOMMENDATIONS', '5'))
#     PREFERENCE_WEIGHT = float(os.getenv('PREFERENCE_WEIGHT', '0.7'))
    
#     # Language mappings for better support
#     LANGUAGE_NAMES = {
#         'en': 'English',
#         'hi': 'Hindi',
#         'pa': 'Punjabi'
#     }
    
#     # Job categories for PGRKAM platform
#     JOB_CATEGORIES = [
#         'Government Jobs',
#         'Private Sector',
#         'Skill Development',
#         'Foreign Counseling',
#         'Education',
#         'Healthcare',
#         'Technology',
#         'Agriculture',
#         'Banking',
#         'Defense'
#     ]
    
#     # Skill development areas
#     SKILL_AREAS = [
#         'Digital Literacy',
#         'Communication Skills',
#         'Technical Skills',
#         'Language Learning',
#         'Leadership',
#         'Entrepreneurship',
#         'Computer Skills',
#         'Soft Skills'
#     ]
