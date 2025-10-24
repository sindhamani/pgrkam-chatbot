# flask_app.py (Test Code)
from flask import Flask, jsonify
import datetime

app = Flask(__name__)

@app.route('/')
def hello():
    """Returns a simple test message."""
    return jsonify({
        "message": "Hello World! API is responding.",
        "timestamp_utc": datetime.datetime.utcnow().isoformat()
    })

# Note: The if __name__ == '__main__': block is not needed for Gunicorn deployment

# import os
# import logging
# from datetime import datetime
# from flask import Flask, request, jsonify
# from flask_cors import CORS

# # Assuming gemini_chatbot.py and config.py are in the same directory
# try:
#     from gemini_chatbot import GeminiChatbot
#     from config import Config
# except ImportError as e:
#     logging.error(f"Error importing required modules: {e}")
#     GeminiChatbot = None # Define as None if import fails

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Initialize Flask app
# app = Flask(__name__)

# # Configure CORS more specifically
# # Allows requests ONLY from your Hostinger domain
# CORS(app, resources={
#     r"/api/*": {"origins": ["https://pkgassist.site", "http://pkgassist.site"]},
#     r"/health": {"origins": ["https://pkgassist.site", "http://pkgassist.site"]}
# })

# # Initialize chatbot
# try:
#     if GeminiChatbot:
#         chatbot = GeminiChatbot()
#         logger.info("Chatbot initialized successfully")
#     else:
#         raise RuntimeError("GeminiChatbot class could not be imported.")
# except Exception as e:
#     logger.error(f"Failed to initialize chatbot: {e}")
#     chatbot = None # Indicate failure

# # --- API Endpoints ---

# @app.route('/')
# def root():
#     """Simple root endpoint confirming the API is live."""
#     return jsonify({
#         "message": "PGRKAM Backend API is running!",
#         "status": "active" if chatbot else "degraded (chatbot init failed)",
#         "timestamp_utc": datetime.utcnow().isoformat(),
#         "endpoints": ["/health", "/api/chat", "/api/recommendations", "/api/preferences", "/api/history"]
#     })

# @app.route('/health')
# def health_check():
#     """Health check endpoint"""
#     return jsonify({
#         'status': 'healthy' if chatbot else 'unhealthy',
#         'timestamp_utc': datetime.utcnow().isoformat(),
#         'chatbot_available': chatbot is not None
#     })

# @app.route('/api/chat', methods=['POST'])
# def chat():
#     """Handle chat requests"""
#     if not chatbot:
#         logger.warning("Chat request received but chatbot is unavailable.")
#         return jsonify({
#             'error': 'Chatbot not available',
#             'reply': 'Service temporarily unavailable. Please try again later.'
#         }), 503 # Service Unavailable

#     try:
#         data = request.get_json()
#         if not data:
#             logger.warning("Chat request received with no JSON data.")
#             return jsonify({'error': 'Invalid JSON data'}), 400

#         query = data.get('query', '').strip()
#         language = data.get('language', 'en')
#         session_id = data.get('session_id', 'default_api_session') # Use a different default for API
#         input_type = data.get('input_type', 'text')

#         logger.info(f"Received chat query for session '{session_id}': '{query[:50]}...'")

#         if not query:
#             logger.warning(f"Empty query received for session '{session_id}'.")
#             return jsonify({
#                 'error': 'Empty query',
#                 'reply': 'Please provide a question.'
#             }), 400

#         # Process the query using the chatbot instance
#         result = chatbot.process_query(query, session_id, language, input_type)

#         logger.info(f"Sending reply for session '{session_id}': '{result.get('response', '')[:50]}...'")
#         return jsonify(result)

#     except Exception as e:
#         logger.error(f"Chat API error processing request for session '{session_id}': {e}", exc_info=True) # Log traceback
#         return jsonify({
#             'error': 'Internal server error',
#             'reply': 'I apologize, but I encountered an error processing your request.'
#         }), 500

# # --- Other API Endpoints (Keep as they were) ---

# @app.route('/api/recommendations', methods=['GET'])
# def get_recommendations():
#     if not chatbot: return jsonify({'error': 'Chatbot not available'}), 503
#     session_id = request.args.get('session_id', 'default_api_session')
#     category = request.args.get('category')
#     try:
#         recommendations = chatbot.recommend_jobs(session_id, f"Find jobs in {category}" if category else "Find jobs")
#         return jsonify({'recommendations': recommendations, 'session_id': session_id})
#     except Exception as e:
#         logger.error(f"Recommendations API error: {e}", exc_info=True)
#         return jsonify({'error': 'Internal server error fetching recommendations'}), 500

# @app.route('/api/preferences', methods=['GET', 'PUT'])
# def handle_preferences():
#     if not chatbot: return jsonify({'error': 'Chatbot not available'}), 503
#     session_id = request.args.get('session_id') or (request.json and request.json.get('session_id'))
#     if not session_id: return jsonify({'error': 'session_id is required'}), 400

#     try:
#         if request.method == 'GET':
#             preferences = chatbot.get_user_preferences(session_id)
#             return jsonify({'preferences': preferences})
#         elif request.method == 'PUT':
#             data = request.get_json()
#             if not data: return jsonify({'error': 'Invalid JSON data'}), 400
#             preferences = data.get('preferences', {})
#             chatbot.update_user_preferences(session_id, preferences)
#             return jsonify({'message': 'Preferences updated successfully'})
#     except Exception as e:
#         logger.error(f"Preferences API error: {e}", exc_info=True)
#         return jsonify({'error': 'Internal server error handling preferences'}), 500


# @app.route('/api/history', methods=['GET'])
# def get_history():
#     if not chatbot: return jsonify({'error': 'Chatbot not available'}), 503
#     session_id = request.args.get('session_id', 'default_api_session')
#     try:
#         limit = int(request.args.get('limit', 10))
#         history = chatbot.get_conversation_history(session_id, limit)
#         return jsonify({'history': history, 'session_id': session_id})
#     except ValueError:
#          return jsonify({'error': 'Invalid limit parameter, must be an integer.'}), 400
#     except Exception as e:
#         logger.error(f"History API error: {e}", exc_info=True)
#         return jsonify({'error': 'Internal server error fetching history'}), 500


# # Gunicorn runs the 'app' object directly, so this part is only for local testing
# if __name__ == '__main__':
#     # Use a different port for local testing if 8000 is used by Gunicorn/Nginx
#     local_port = int(os.environ.get('PORT', 8081))
#     print(f"Starting Flask development server on http://localhost:{local_port}")
#     app.run(host='0.0.0.0', port=local_port, debug=True)