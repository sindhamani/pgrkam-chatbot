import os
import sqlite3
import json
import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import logging

# Google AI and Cloud dependencies
import google.generativeai as genai
from google.cloud import firestore
from google.cloud import storage
from google.cloud import aiplatform
from google.cloud.sql.connector import Connector
import sqlalchemy

# Multilingual support
from googletrans import Translator
from langdetect import detect
import unicodedata

# Speech processing
import speech_recognition as sr
import pyttsx3

# Database and utilities
import pandas as pd
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiChatbot:
    """Enhanced multilingual chatbot using Google Gemini API for PGRKAM digital platform"""
    
    def __init__(self):
        self.config = Config()
        self.translator = Translator()
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        self.setup_gemini()
        self.setup_tts()
        self.setup_database()
        self.setup_vector_store()
        
    def setup_gemini(self):
        """Configure Google Gemini API"""
        try:
            genai.configure(api_key=self.config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(self.config.GEMINI_MODEL)
            logger.info("Gemini API configured successfully")
        except Exception as e:
            logger.error(f"Error configuring Gemini API: {e}")
            raise
    
    def setup_tts(self):
        """Configure text-to-speech engine"""
        self.tts_engine.setProperty('rate', self.config.SPEECH_RATE)
        self.tts_engine.setProperty('volume', self.config.SPEECH_VOLUME)
        
        # Try to set voice gender
        voices = self.tts_engine.getProperty('voices')
        if voices:
            if self.config.VOICE_GENDER.lower() == 'female':
                for voice in voices:
                    if 'female' in voice.name.lower() or 'woman' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
            else:
                for voice in voices:
                    if 'male' in voice.name.lower() or 'man' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
    
    def setup_database(self):
        """Initialize database - supports both SQLite and Cloud SQL"""
        try:
            if self.config.CLOUD_SQL_CONNECTION_NAME:
                # Use Cloud SQL for production
                self.setup_cloud_sql()
            else:
                # Use local SQLite for development
                self.setup_local_database()
            
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database setup error: {e}")
            # Fallback to local SQLite
            self.setup_local_database()
    
    def setup_local_database(self):
        """Setup local SQLite database"""
        self.conn = sqlite3.connect('chatbot.db')
        cursor = self.conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                preferred_language TEXT DEFAULT 'en',
                preferences TEXT DEFAULT '{}'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                query TEXT,
                response TEXT,
                language TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                query_type TEXT DEFAULT 'text',
                FOREIGN KEY (session_id) REFERENCES users (session_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                category TEXT,
                keywords TEXT,
                location TEXT,
                experience_level TEXT,
                FOREIGN KEY (session_id) REFERENCES users (session_id)
            )
        ''')
        
        self.conn.commit()
    
    def setup_cloud_sql(self):
        """Setup Google Cloud SQL database"""
        try:
            # Initialize Cloud SQL connector
            connector = Connector()
            
            # Create connection to Cloud SQL
            def getconn():
                conn = connector.connect(
                    self.config.CLOUD_SQL_CONNECTION_NAME,
                    "pg8000",
                    user=os.getenv('DB_USER', 'postgres'),
                    password=os.getenv('DB_PASSWORD', ''),
                    db=os.getenv('DB_NAME', 'chatbot')
                )
                return conn
            
            # Create SQLAlchemy engine
            self.engine = sqlalchemy.create_engine(
                "postgresql+pg8000://",
                creator=getconn,
            )
            
            # Create tables
            with self.engine.connect() as conn:
                conn.execute(sqlalchemy.text('''
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        session_id VARCHAR(255) UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        preferred_language VARCHAR(10) DEFAULT 'en',
                        preferences TEXT DEFAULT '{}'
                    )
                '''))
                
                conn.execute(sqlalchemy.text('''
                    CREATE TABLE IF NOT EXISTS conversations (
                        id SERIAL PRIMARY KEY,
                        session_id VARCHAR(255),
                        query TEXT,
                        response TEXT,
                        language VARCHAR(10),
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        query_type VARCHAR(20) DEFAULT 'text',
                        FOREIGN KEY (session_id) REFERENCES users (session_id)
                    )
                '''))
                
                conn.execute(sqlalchemy.text('''
                    CREATE TABLE IF NOT EXISTS job_preferences (
                        id SERIAL PRIMARY KEY,
                        session_id VARCHAR(255),
                        category VARCHAR(100),
                        keywords TEXT,
                        location VARCHAR(100),
                        experience_level VARCHAR(50),
                        FOREIGN KEY (session_id) REFERENCES users (session_id)
                    )
                '''))
                
                conn.commit()
            
            logger.info("Cloud SQL database initialized")
            
        except Exception as e:
            logger.error(f"Cloud SQL setup error: {e}")
            raise
    
    def setup_vector_store(self):
        """Initialize vector store using Google Cloud alternatives"""
        try:
            if self.config.USE_VERTEX_AI:
                # Use Vertex AI for embeddings and vector search
                aiplatform.init(
                    project=self.config.PROJECT_ID,
                    location=self.config.LOCATION
                )
                logger.info("Vertex AI initialized for vector store")
            else:
                # Use Firestore for simple document storage
                self.db = firestore.Client(project=self.config.PROJECT_ID)
                logger.info("Firestore initialized for document storage")
            
        except Exception as e:
            logger.error(f"Vector store setup error: {e}")
            # Continue without vector store for basic functionality
    
    def detect_language(self, text: str) -> str:
        """Detect the language of input text"""
        try:
            # Remove special characters and normalize
            clean_text = re.sub(r'[^\w\s]', '', text)
            if len(clean_text) < 3:
                return self.config.DEFAULT_LANGUAGE
                
            detected = detect(clean_text)
            
            # Map detected language to supported languages
            if detected in ['hi', 'pa']:
                return detected
            elif detected == 'en':
                return 'en'
            else:
                return self.config.DEFAULT_LANGUAGE
                
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return self.config.DEFAULT_LANGUAGE
    
    def translate_text(self, text: str, target_lang: str, source_lang: str = None) -> str:
        """Translate text to target language"""
        try:
            if source_lang and source_lang == target_lang:
                return text
                
            result = self.translator.translate(text, dest=target_lang, src=source_lang)
            return result.text
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text
    
    def process_voice_input(self, language: str = 'en') -> str:
        """Process voice input using speech recognition"""
        try:
            with sr.Microphone() as source:
                print("Listening...")
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=5)
                
            # Use appropriate language for recognition
            lang_codes = {
                'en': 'en-US',
                'hi': 'hi-IN',
                'pa': 'pa-IN'
            }
            
            lang_code = lang_codes.get(language, 'en-US')
            text = self.recognizer.recognize_google(audio, language=lang_code)
            return text
            
        except sr.WaitTimeoutError:
            return "No voice input detected"
        except sr.UnknownValueError:
            return "Could not understand the audio"
        except Exception as e:
            logger.error(f"Voice recognition error: {e}")
            return "Voice recognition failed"
    
    def speak_text(self, text: str):
        """Convert text to speech"""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            logger.error(f"Text-to-speech error: {e}")
    
    def get_similar_documents(self, query: str, k: int = None) -> List:
        """Retrieve similar documents using vector search"""
        if k is None:
            k = self.config.TOP_K_RESULTS
            
        try:
            if self.config.USE_VERTEX_AI:
                # Use Vertex AI for similarity search
                # This is a simplified implementation
                # In production, you'd use Vertex AI Search or Matching Engine
                return []
            else:
                # Use Firestore for simple text search
                docs_ref = self.db.collection('documents')
                docs = docs_ref.where('content', '>=', query).limit(k).stream()
                return [doc.to_dict() for doc in docs]
                
        except Exception as e:
            logger.error(f"Vector search error: {e}")
            return []
    
    def generate_response(self, query: str, context_docs: List, language: str) -> str:
        """Generate response using Gemini with context"""
        try:
            # Create context from retrieved documents
            context = "\n".join([doc.get('content', '') if isinstance(doc, dict) else str(doc) for doc in context_docs])
            
            # Create language-specific prompt
            prompts = {
                'en': f"""
                You are a helpful assistant for the PGRKAM (Punjab Government Recruitment and Knowledge Acquisition Mission) digital platform. 
                Answer the following question based on the provided context about job search, skill development, and foreign counseling.
                
                Context: {context}
                
                Question: {query}
                
                Provide a helpful, accurate response. If the information is not in the context, say so politely and provide general guidance.
                """,
                'hi': f"""
                आप PGRKAM (पंजाब सरकार भर्ती और ज्ञान अधिग्रहण मिशन) डिजिटल प्लेटफॉर्म के लिए एक सहायक हैं।
                नौकरी खोज, कौशल विकास और विदेशी परामर्श के बारे में प्रदान की गई जानकारी के आधार पर निम्नलिखित प्रश्न का उत्तर दें।
                
                संदर्भ: {context}
                
                प्रश्न: {query}
                
                एक सहायक, सटीक प्रतिक्रिया प्रदान करें। यदि जानकारी संदर्भ में नहीं है, तो विनम्रता से कहें और सामान्य मार्गदर्शन दें।
                """,
                'pa': f"""
                ਤੁਸੀਂ PGRKAM (ਪੰਜਾਬ ਸਰਕਾਰ ਭਰਤੀ ਅਤੇ ਗਿਆਨ ਪ੍ਰਾਪਤੀ ਮਿਸ਼ਨ) ਡਿਜੀਟਲ ਪਲੇਟਫਾਰਮ ਲਈ ਇੱਕ ਸਹਾਇਕ ਹੋ।
                ਨੌਕਰੀ ਖੋਜ, ਹੁਨਰ ਵਿਕਾਸ ਅਤੇ ਵਿਦੇਸ਼ੀ ਸਲਾਹ ਮਸ਼ਵਰੇ ਬਾਰੇ ਪ੍ਰਦਾਨ ਕੀਤੀ ਗਈ ਜਾਣਕਾਰੀ ਦੇ ਆਧਾਰ 'ਤੇ ਹੇਠਾਂ ਦਿੱਤੇ ਸਵਾਲ ਦਾ ਜਵਾਬ ਦਿਓ।
                
                ਸੰਦਰਭ: {context}
                
                ਸਵਾਲ: {query}
                
                ਇੱਕ ਸਹਾਇਕ, ਸਹੀ ਜਵਾਬ ਪ੍ਰਦਾਨ ਕਰੋ। ਜੇ ਜਾਣਕਾਰੀ ਸੰਦਰਭ ਵਿੱਚ ਨਹੀਂ ਹੈ, ਤਾਂ ਨਮਰਤਾ ਨਾਲ ਕਹੋ ਅਤੇ ਆਮ ਗਾਈਡੇਂਸ ਦਿਓ।
                """
            }
            
            prompt = prompts.get(language, prompts['en'])
            
            # Generate response using Gemini
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.config.MAX_TOKENS,
                    temperature=self.config.TEMPERATURE,
                )
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            return "I apologize, but I'm having trouble generating a response at the moment."
    
    def save_conversation(self, session_id: str, query: str, response: str, 
                         language: str, query_type: str = 'text'):
        """Save conversation to database"""
        try:
            if self.config.CLOUD_SQL_CONNECTION_NAME:
                # Save to Cloud SQL
                with self.engine.connect() as conn:
                    conn.execute(sqlalchemy.text('''
                        INSERT INTO conversations (session_id, query, response, language, query_type)
                        VALUES (:session_id, :query, :response, :language, :query_type)
                    '''), {
                        'session_id': session_id,
                        'query': query,
                        'response': response,
                        'language': language,
                        'query_type': query_type
                    })
                    conn.commit()
            else:
                # Save to local SQLite
                cursor = self.conn.cursor()
                cursor.execute('''
                    INSERT INTO conversations (session_id, query, response, language, query_type)
                    VALUES (?, ?, ?, ?, ?)
                ''', (session_id, query, response, language, query_type))
                self.conn.commit()
                
        except Exception as e:
            logger.error(f"Database save error: {e}")
    
    def get_user_preferences(self, session_id: str) -> Dict:
        """Get user preferences from database"""
        try:
            if self.config.CLOUD_SQL_CONNECTION_NAME:
                # Get from Cloud SQL
                with self.engine.connect() as conn:
                    result = conn.execute(sqlalchemy.text('''
                        SELECT preferences FROM users WHERE session_id = :session_id
                    '''), {'session_id': session_id}).fetchone()
                    
                    if result:
                        return json.loads(result[0])
                    return {}
            else:
                # Get from local SQLite
                cursor = self.conn.cursor()
                cursor.execute('SELECT preferences FROM users WHERE session_id = ?', (session_id,))
                result = cursor.fetchone()
                
                if result:
                    return json.loads(result[0])
                return {}
                
        except Exception as e:
            logger.error(f"Error getting preferences: {e}")
            return {}
    
    def update_user_preferences(self, session_id: str, preferences: Dict):
        """Update user preferences in database"""
        try:
            if self.config.CLOUD_SQL_CONNECTION_NAME:
                # Update Cloud SQL
                with self.engine.connect() as conn:
                    conn.execute(sqlalchemy.text('''
                        INSERT INTO users (session_id, preferences)
                        VALUES (:session_id, :preferences)
                        ON CONFLICT (session_id) DO UPDATE SET preferences = :preferences
                    '''), {
                        'session_id': session_id,
                        'preferences': json.dumps(preferences)
                    })
                    conn.commit()
            else:
                # Update local SQLite
                cursor = self.conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO users (session_id, preferences)
                    VALUES (?, ?)
                ''', (session_id, json.dumps(preferences)))
                self.conn.commit()
                
        except Exception as e:
            logger.error(f"Error updating preferences: {e}")
    
    def recommend_jobs(self, session_id: str, query: str) -> List[Dict]:
        """Generate job recommendations based on user preferences and query"""
        try:
            preferences = self.get_user_preferences(session_id)
            
            # Enhanced job recommendations for PGRKAM
            job_recommendations = [
                {
                    'title': 'Software Developer',
                    'company': 'Tech Corp India',
                    'location': 'Chandigarh',
                    'category': 'Technology',
                    'experience': '2-5 years',
                    'description': 'Looking for skilled software developers with Python experience.',
                    'salary': '₹4-8 LPA',
                    'application_deadline': '2024-12-31'
                },
                {
                    'title': 'Administrative Officer',
                    'company': 'Punjab Government',
                    'location': 'Various Locations',
                    'category': 'Government Jobs',
                    'experience': '1-3 years',
                    'description': 'Administrative officer position in Punjab government departments.',
                    'salary': '₹3-5 LPA',
                    'application_deadline': '2024-12-15'
                },
                {
                    'title': 'Skill Development Trainer',
                    'company': 'Punjab Skill Development Mission',
                    'location': 'Ludhiana',
                    'category': 'Skill Development',
                    'experience': '3-7 years',
                    'description': 'Trainer for digital literacy and communication skills programs.',
                    'salary': '₹3-6 LPA',
                    'application_deadline': '2024-12-20'
                },
                {
                    'title': 'Foreign Education Counselor',
                    'company': 'PGRKAM Counseling Center',
                    'location': 'Amritsar',
                    'category': 'Foreign Counseling',
                    'experience': '2-4 years',
                    'description': 'Guide students for study abroad opportunities and visa applications.',
                    'salary': '₹3-5 LPA',
                    'application_deadline': '2024-12-25'
                }
            ]
            
            # Filter based on preferences
            filtered_jobs = []
            for job in job_recommendations:
                if preferences.get('preferred_category') and job['category'] == preferences['preferred_category']:
                    filtered_jobs.append(job)
                elif not preferences.get('preferred_category'):
                    filtered_jobs.append(job)
            
            return filtered_jobs[:self.config.MAX_JOB_RECOMMENDATIONS]
            
        except Exception as e:
            logger.error(f"Job recommendation error: {e}")
            return []
    
    def process_query(self, query: str, session_id: str = 'default', 
                     language: str = None, input_type: str = 'text') -> Dict:
        """Main method to process user queries"""
        try:
            # Detect language if not provided
            if not language:
                language = self.detect_language(query)
            
            # Get or create user preferences
            preferences = self.get_user_preferences(session_id)
            if not preferences:
                preferences = {
                    'preferred_language': language,
                    'preferred_category': None,
                    'experience_level': None
                }
                self.update_user_preferences(session_id, preferences)
            
            # Get similar documents for context
            context_docs = self.get_similar_documents(query)
            
            # Generate response
            response = self.generate_response(query, context_docs, language)
            
            # Check if query is about jobs and provide recommendations
            job_keywords = ['job', 'naukri', 'ਨੌਕਰੀ', 'career', 'employment', 'vacancy', 'position']
            if any(keyword in query.lower() for keyword in job_keywords):
                job_recommendations = self.recommend_jobs(session_id, query)
                if job_recommendations:
                    response += "\n\n🎯 Job Recommendations:\n"
                    for i, job in enumerate(job_recommendations, 1):
                        response += f"{i}. **{job['title']}** at {job['company']}\n"
                        response += f"   📍 Location: {job['location']}\n"
                        response += f"   💼 Experience: {job['experience']}\n"
                        response += f"   💰 Salary: {job['salary']}\n"
                        response += f"   📅 Deadline: {job['application_deadline']}\n\n"
            
            # Save conversation
            self.save_conversation(session_id, query, response, language, input_type)
            
            return {
                'response': response,
                'language': language,
                'input_type': input_type,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Query processing error: {e}")
            return {
                'response': "I apologize, but I encountered an error processing your request.",
                'language': language or 'en',
                'input_type': input_type,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Get conversation history for a session"""
        try:
            if self.config.CLOUD_SQL_CONNECTION_NAME:
                # Get from Cloud SQL
                with self.engine.connect() as conn:
                    result = conn.execute(sqlalchemy.text('''
                        SELECT query, response, language, timestamp, query_type
                        FROM conversations 
                        WHERE session_id = :session_id 
                        ORDER BY timestamp DESC 
                        LIMIT :limit
                    '''), {'session_id': session_id, 'limit': limit}).fetchall()
                    
                    history = []
                    for row in result:
                        history.append({
                            'query': row[0],
                            'response': row[1],
                            'language': row[2],
                            'timestamp': row[3],
                            'query_type': row[4]
                        })
                    
                    return history
            else:
                # Get from local SQLite
                cursor = self.conn.cursor()
                cursor.execute('''
                    SELECT query, response, language, timestamp, query_type
                    FROM conversations 
                    WHERE session_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (session_id, limit))
                
                history = []
                for row in cursor.fetchall():
                    history.append({
                        'query': row[0],
                        'response': row[1],
                        'language': row[2],
                        'timestamp': row[3],
                        'query_type': row[4]
                    })
                
                return history
                
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []

if __name__ == "__main__":
    # Example usage
    chatbot = GeminiChatbot()
    
    print("PGRKAM Digital Assistant - Gemini-Powered Chatbot")
    print("Supported languages: English, Hindi, Punjabi")
    print("Type 'voice' for voice input, 'history' for conversation history, 'quit' to exit")
    print("-" * 60)
    
    session_id = "demo_session"
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == 'quit':
            break
        elif user_input.lower() == 'voice':
            print("Speak now...")
            voice_text = chatbot.process_voice_input('en')
            print(f"Voice input: {voice_text}")
            if voice_text and "failed" not in voice_text.lower():
                result = chatbot.process_query(voice_text, session_id, input_type='voice')
                print(f"Assistant: {result['response']}")
                chatbot.speak_text(result['response'])
        elif user_input.lower() == 'history':
            history = chatbot.get_conversation_history(session_id)
            print("\nConversation History:")
            for conv in history:
                print(f"[{conv['timestamp']}] {conv['query_type']}: {conv['query']}")
                print(f"Response: {conv['response'][:100]}...")
                print("-" * 40)
        else:
            result = chatbot.process_query(user_input, session_id)
            print(f"Assistant: {result['response']}")
