import os
import sqlite3
import json
import re
from datetime import datetime
from typing import List, Dict, Optional
import logging

# --- Use Vertex AI SDK ---
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

# Other Google Cloud dependencies (keep if needed for RAG later)
# from google.cloud import firestore
# from google.cloud import storage

# Multilingual support
#from googletrans import Translator
#from langdetect import detect

# Configuration
from config import Config # Make sure config.py exists and is correct

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GeminiChatbot:
    """Streamlined multilingual chatbot using Google Vertex AI (Gemini)"""

    def __init__(self):
        self.config = Config()
        #self.translator = Translator()
        self.setup_vertex_ai()
        self.setup_local_database()
        self.setup_vector_store() # Placeholder

    def setup_vertex_ai(self):
        """Configure Google Vertex AI (Gemini)"""
        try:
            PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", self.config.PROJECT_ID)
            LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", self.config.LOCATION)

            if not PROJECT_ID:
                raise ValueError("GOOGLE_CLOUD_PROJECT not set in config or environment.")

            vertexai.init(project=PROJECT_ID, location=LOCATION)
            # Ensure config.GEMINI_MODEL is correctly set (e.g., "gemini-1.0-pro")
            self.model = GenerativeModel(self.config.GEMINI_MODEL)
            logger.info(f"Vertex AI initialized successfully in project {PROJECT_ID}, location {LOCATION} with model {self.config.GEMINI_MODEL}")
        except Exception as e:
            logger.error(f"Error configuring Vertex AI: {e}", exc_info=True)
            self.model = None
            raise

    def setup_local_database(self):
        """Setup local SQLite database"""
        db_path = getattr(self.config, 'SQLITE_DB_PATH', 'chatbot.db') # Get path from config or default
        try:
            # check_same_thread=False allows multiple web requests to use the same connection
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            cursor = self.conn.cursor()
            # Create tables if they don't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    preferred_language TEXT DEFAULT 'en',
                    preferences TEXT DEFAULT '{}'
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    query TEXT,
                    response TEXT,
                    language TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES users (session_id)
                )
            ''')
            # Removed job_preferences table for simplicity, can be added back if needed
            self.conn.commit()
            logger.info(f"SQLite database initialized at {db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize SQLite database at {db_path}: {e}", exc_info=True)
            self.conn = None

    def setup_vector_store(self):
        """Initialize vector store - Basic Placeholder"""
        # In a real RAG setup, you'd initialize connection to Vector DB or Search here
        logger.info("Vector store setup placeholder. RAG features are currently basic.")
        self.vector_store_active = False # Flag to indicate if RAG is ready

    # def detect_language(self, text: str) -> str:
    #     """Detect language, default to English on error or short text"""
    #     try:
    #         clean_text = re.sub(r'[^\w\s]', '', text).strip()
    #         if len(clean_text) < 5: # Require a bit more text for reliable detection
    #             return self.config.DEFAULT_LANGUAGE
    #         detected = detect(clean_text)
    #         if detected in ['hi', 'pa', 'en']:
    #             return detected
    #         else:
    #              # If detected language isn't supported, try translation check or default
    #              logger.warning(f"Detected unsupported language '{detected}'. Defaulting.")
    #              return self.config.DEFAULT_LANGUAGE
    #     except Exception as e:
    #         logger.error(f"Language detection error: {e}")
    #         return self.config.DEFAULT_LANGUAGE

    # def translate_text(self, text: str, target_lang: str, source_lang: Optional[str] = None) -> str:
    #     """Translate text if source and target are different"""
    #     effective_source = source_lang or self.detect_language(text)
    #     if effective_source == target_lang:
    #         return text
    #     try:
    #         result = self.translator.translate(text, dest=target_lang, src=effective_source)
    #         return result.text
    #     except Exception as e:
    #         logger.error(f"Translation error from '{effective_source}' to '{target_lang}': {e}")
    #         return text # Return original text on error

    def get_similar_documents(self, query: str, k: int = 3) -> List:
        """Retrieve similar documents - Placeholder"""
        if self.vector_store_active:
            logger.info(f"Searching vector store for: '{query[:50]}...'")
            # --- Add your actual vector search logic here ---
            # Example: results = vector_db.similarity_search(query, k=k)
            # return results
            pass
        logger.debug("No active vector store for RAG.")
        return [] # Return empty list if RAG is not active

    def generate_response(self, query: str, context_docs: List, language: str) -> str:
        """Generate response using Vertex AI (Gemini) with context"""
        if not self.model:
            logger.error("Gemini model not initialized.")
            return "AI model unavailable."
        try:
            # Build context string safely
            context_parts = [doc.get('content', '') for doc in context_docs if isinstance(doc, dict) and 'content' in doc]
            context = "\n".join(context_parts).strip()
            if context:
                 logger.info(f"Using {len(context_docs)} documents for context.")
                 context_prompt_part = f"Context:\n{context}\n"
            else:
                 context_prompt_part = "Context: No relevant documents found.\n"


            # Define prompts
            prompts = {
                 'en': f"You are a helpful assistant for PGRKAM. Answer the user's question based ONLY on the provided context if available. If not, provide general guidance relevant to PGRKAM's services (job search, skills, foreign counseling in Punjab).\n\n{context_prompt_part}\nQuestion: {query}\n\nAnswer in English:",
                 'hi': f"आप PGRKAM के सहायक हैं। केवल दिए गए संदर्भ के आधार पर उत्तर दें यदि उपलब्ध हो। यदि नहीं, तो PGRKAM सेवाओं (पंजाब में नौकरी खोज, कौशल, विदेशी परामर्श) से संबंधित सामान्य मार्गदर्शन प्रदान करें।\n\n{context_prompt_part}\nप्रश्न: {query}\n\nउत्तर हिंदी में दें:",
                 'pa': f"ਤੁਸੀਂ PGRKAM ਲਈ ਸਹਾਇਕ ਹੋ। ਸਿਰਫ਼ ਦਿੱਤੇ ਸੰਦਰਭ ਦੇ ਆਧਾਰ 'ਤੇ ਜਵਾਬ ਦਿਓ ਜੇਕਰ ਉਪਲਬਧ ਹੋਵੇ। ਜੇਕਰ ਨਹੀਂ, ਤਾਂ PGRKAM ਸੇਵਾਵਾਂ (ਪੰਜਾਬ ਵਿੱਚ ਨੌਕਰੀ ਦੀ ਖੋਜ, ਹੁਨਰ, ਵਿਦੇਸ਼ੀ ਸਲਾਹ) ਨਾਲ ਸੰਬੰਧਿਤ ਆਮ ਮਾਰਗਦਰਸ਼ਨ ਪ੍ਰਦਾਨ ਕਰੋ।\n\n{context_prompt_part}\nਸਵਾਲ: {query}\n\nਜਵਾਬ ਪੰਜਾਬੀ ਵਿੱਚ ਦਿਓ:"
            }
            prompt = prompts.get(language, prompts['en'])

            # Configure generation parameters from config
            generation_config = GenerationConfig(
                max_output_tokens=getattr(self.config, 'MAX_TOKENS', 1024),
                temperature=getattr(self.config, 'TEMPERATURE', 0.7),
            )

            # Generate response
            response = self.model.generate_content(prompt, generation_config=generation_config)
            
            # Check for safety ratings or blocked responses if needed
            # if response.prompt_feedback.block_reason: ... handle safety blocks ...
            
            return response.text

        except Exception as e:
            logger.error(f"Vertex AI response generation error: {e}", exc_info=True)
            return "Apologies, I encountered an error generating the response."

    def save_conversation(self, session_id: str, query: str, response: str, language: str):
        """Save conversation to SQLite database"""
        if not self.conn:
            logger.warning("Database connection not available. Skipping conversation save.")
            return
        try:
            cursor = self.conn.cursor()
            # Ensure user exists before saving conversation
            cursor.execute('INSERT OR IGNORE INTO users (session_id, preferred_language) VALUES (?, ?)', (session_id, language))
            # Save conversation
            cursor.execute('''
                INSERT INTO conversations (session_id, query, response, language)
                VALUES (?, ?, ?, ?)
            ''', (session_id, query, response, language))
            self.conn.commit()
            logger.debug(f"Saved conversation for session {session_id}")
        except Exception as e:
            logger.error(f"SQLite save_conversation error: {e}", exc_info=True)

    def get_user_preferences(self, session_id: str) -> Dict:
        """Get user preferences from SQLite"""
        if not self.conn: return {}
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT preferences FROM users WHERE session_id = ?', (session_id,))
            result = cursor.fetchone()
            if result and result[0]:
                try:
                    return json.loads(result[0])
                except json.JSONDecodeError:
                     logger.error(f"Failed to parse preferences JSON for session {session_id}")
                     return {}
            return {} # Return empty dict if no user or no preferences found
        except Exception as e:
             logger.error(f"SQLite get_user_preferences error: {e}", exc_info=True)
             return {}

    def update_user_preferences(self, session_id: str, preferences: Dict):
        """Update user preferences in SQLite"""
        if not self.conn: return
        try:
            cursor = self.conn.cursor()
            # Ensure user exists first, update language if needed
            cursor.execute('INSERT OR IGNORE INTO users (session_id, preferred_language) VALUES (?, ?)',
                           (session_id, preferences.get('preferred_language', self.config.DEFAULT_LANGUAGE)))
            # Update preferences JSON
            cursor.execute('''
                UPDATE users SET preferences = ? WHERE session_id = ?
            ''', (json.dumps(preferences), session_id))
            self.conn.commit()
            logger.info(f"Updated preferences for session {session_id}")
        except Exception as e:
            logger.error(f"SQLite update_user_preferences error: {e}", exc_info=True)

    def process_query(self, query: str, session_id: str = 'default_session', language: Optional[str] = None) -> Dict:
        """Main method to process user text queries"""
        logger.info(f"Processing query for session '{session_id}': '{query[:50]}...'")
        start_time = datetime.now()
        
        # # Determine language
        # processing_language = language or self.detect_language(query)
        # logger.info(f"Processing in language: {processing_language}")

        # Inside the process_query method:

        # --- Remove language detection ---
        # Determine language
        # processing_language = language or self.detect_language(query) # REMOVE THIS LINE

        # --- Replace with simpler logic ---
        processing_language = language or self.config.DEFAULT_LANGUAGE
        if processing_language not in self.config.SUPPORTED_LANGUAGES:
            logger.warning(f"Unsupported language '{processing_language}' requested. Defaulting to {self.config.DEFAULT_LANGUAGE}.")
            processing_language = self.config.DEFAULT_LANGUAGE

        logger.info(f"Processing in language: {processing_language} (Detection disabled)")
        # Get context (RAG - currently returns empty list)
        context_docs = self.get_similar_documents(query)

        # Generate response
        response_text = self.generate_response(query, context_docs, processing_language)

        # Save conversation to DB
        self.save_conversation(session_id, query, response_text, processing_language)

        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        logger.info(f"Query processed in {processing_time:.2f} seconds for session {session_id}")

        return {
            'response': response_text,
            'language': processing_language,
            'session_id': session_id,
            'timestamp': end_time.isoformat()
        }

    # Removed get_conversation_history and recommend_jobs for simplicity
    # They can be added back, ensuring they use the SQLite connection (self.conn)