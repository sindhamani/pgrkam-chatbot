import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the PGRKAM Digital Assistant"""
    
    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
    
    # Vector Store Configuration (using Google Cloud alternatives)
    USE_VERTEX_AI = os.getenv('USE_VERTEX_AI', 'False').lower() == 'true'
    PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT', '')
    LOCATION = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///chatbot.db')
    
    # Application Settings
    APP_NAME = os.getenv('APP_NAME', 'PGRKAM Digital Assistant')
    APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Language Settings
    DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE', 'en')
    SUPPORTED_LANGUAGES = os.getenv('SUPPORTED_LANGUAGES', 'en,hi,pa').split(',')
    
    # Audio Settings
    SPEECH_RATE = int(os.getenv('SPEECH_RATE', '150'))
    SPEECH_VOLUME = float(os.getenv('SPEECH_VOLUME', '0.8'))
    VOICE_GENDER = os.getenv('VOICE_GENDER', 'male')
    
    # RAG Settings
    CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '1000'))
    CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '200'))
    TOP_K_RESULTS = int(os.getenv('TOP_K_RESULTS', '3'))
    
    # Gemini Model Settings
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-pro')
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '2048'))
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))
    
    # Google Cloud Settings
    CLOUD_SQL_CONNECTION_NAME = os.getenv('CLOUD_SQL_CONNECTION_NAME', '')
    CLOUD_STORAGE_BUCKET = os.getenv('CLOUD_STORAGE_BUCKET', '')
    
    # Job Recommendation Settings
    MAX_JOB_RECOMMENDATIONS = int(os.getenv('MAX_JOB_RECOMMENDATIONS', '5'))
    PREFERENCE_WEIGHT = float(os.getenv('PREFERENCE_WEIGHT', '0.7'))
    
    # Language mappings for better support
    LANGUAGE_NAMES = {
        'en': 'English',
        'hi': 'Hindi',
        'pa': 'Punjabi'
    }
    
    # Job categories for PGRKAM platform
    JOB_CATEGORIES = [
        'Government Jobs',
        'Private Sector',
        'Skill Development',
        'Foreign Counseling',
        'Education',
        'Healthcare',
        'Technology',
        'Agriculture',
        'Banking',
        'Defense'
    ]
    
    # Skill development areas
    SKILL_AREAS = [
        'Digital Literacy',
        'Communication Skills',
        'Technical Skills',
        'Language Learning',
        'Leadership',
        'Entrepreneurship',
        'Computer Skills',
        'Soft Skills'
    ]
