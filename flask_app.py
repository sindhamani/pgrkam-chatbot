# flask_app.py (with embedded test GUI)
import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

# Import the specific chatbot class
try:
    from gemini_chatbot import GeminiChatbot
    from config import Config
except ImportError as e:
    logging.critical(f"CRITICAL: Failed to import core modules: {e}")
    GeminiChatbot = None

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure CORS (allow requests *from* this page to itself and potentially Hostinger)
origins = ["https://pkgassist.site", "http://pkgassist.site", "https://api.pkgassist.site"] # Add API domain
CORS(app, resources={r"/*": {"origins": origins}})

# Initialize chatbot safely
chatbot_instance = None
if GeminiChatbot:
    try:
        chatbot_instance = GeminiChatbot()
        logger.info("Chatbot initialized successfully in Flask app.")
    except Exception as e:
        logger.error(f"FATAL: Chatbot initialization failed in Flask app: {e}", exc_info=True)
else:
     logger.error("FATAL: GeminiChatbot class not imported, cannot initialize chatbot.")


# --- HTML Template for the Test GUI ---
HTML_TEST_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Backend Test</title>
    <style>
        body { font-family: sans-serif; margin: 20px; background-color: #f0f0f0; }
        .chat-container { max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .chat-box { height: 400px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; margin-bottom: 10px; background: #f9f9f9; }
        .message { margin-bottom: 10px; padding: 8px 12px; border-radius: 15px; max-width: 80%; word-wrap: break-word; }
        .user-message { background-color: #d1eaff; margin-left: auto; text-align: right; }
        .bot-message { background-color: #e2e3e5; margin-right: auto; }
        .input-area { display: flex; gap: 10px; }
        #userInput { flex-grow: 1; padding: 10px; border: 1px solid #ccc; border-radius: 4px; }
        #sendButton { padding: 10px 15px; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        #sendButton:hover { background-color: #0056b3; }
        #status { margin-top: 15px; font-size: 0.9em; color: #555; }
    </style>
</head>
<body>
    <div class="chat-container">
        <h2>Backend Test Chat</h2>
        <div class="chat-box" id="chatBox">
             <div class="bot-message">Backend Status: {{ status }}. Type a message to test Gemini.</div>
        </div>
        <div class="input-area">
            <input type="text" id="userInput" placeholder="Type your message..." onkeypress="handleKeyPress(event)">
            <button id="sendButton" onclick="sendMessage()">Send</button>
        </div>
        <div id="status">Ready.</div>
    </div>

    <script>
        const chatBox = document.getElementById('chatBox');
        const userInput = document.getElementById('userInput');
        const sendButton = document.getElementById('sendButton');
        const statusDiv = document.getElementById('status');

        function addMessage(text, senderClass) {
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message', senderClass);
            messageDiv.textContent = text;
            chatBox.appendChild(messageDiv);
            chatBox.scrollTop = chatBox.scrollHeight; // Scroll down
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        async function sendMessage() {
            const message = userInput.value.trim();
            if (!message) return;

            addMessage(message, 'user-message');
            userInput.value = '';
            statusDiv.textContent = 'Sending...';
            sendButton.disabled = true;

            try {
                // Send POST request to the /api/chat endpoint ON THIS SERVER
                const response = await fetch('/api/chat', { // Relative URL works here
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message }) // Send just the message
                });

                const data = await response.json();

                if (response.ok) {
                    addMessage(data.reply || 'No reply received.', 'bot-message');
                    statusDiv.textContent = 'Ready.';
                } else {
                    addMessage(`Error ${response.status}: ${data.error || data.reply || 'Unknown error'}`, 'bot-message');
                    statusDiv.textContent = `Error (${response.status}). Ready.`;
                }

            } catch (error) {
                console.error('Fetch error:', error);
                addMessage(`Network Error: Could not reach backend. ${error}`, 'bot-message');
                statusDiv.textContent = 'Network Error. Ready.';
            } finally {
                 sendButton.disabled = false;
                 userInput.focus();
            }
        }
         // Add initial status message on load
        document.addEventListener('DOMContentLoaded', () => {
             userInput.focus();
        });
    </script>
</body>
</html>
"""

# --- API Endpoints ---

@app.route('/')
def root():
    """Serve the test HTML chat interface."""
    backend_status = "Active" if chatbot_instance else "Chatbot Init Failed"
    return render_template_string(HTML_TEST_TEMPLATE, status=backend_status)


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests (remains the same)"""
    if not chatbot_instance:
        return jsonify({'error': 'Chatbot not available', 'reply': 'Service temporarily unavailable.'}), 503

    try:
        data = request.get_json()
        if not data: return jsonify({'error': 'Invalid JSON data'}), 400

        query = data.get('message', '').strip() # Changed from 'query' to 'message' to match JS
        language = data.get('language')
        session_id = data.get('session_id', 'test_gui_session') # Use a specific session for GUI

        if not query: return jsonify({'error': 'Empty message', 'reply': 'Please provide a question.'}), 400

        logger.info(f"API Test GUI: Received query for session '{session_id}': '{query[:50]}...'")
        result = chatbot_instance.process_query(query, session_id, language)
        logger.info(f"API Test GUI: Sending reply for session '{session_id}': '{result.get('response', '')[:50]}...'")

        return jsonify({"reply": result.get('response', 'Error retrieving response.')})

    except Exception as e:
        logger.error(f"API Test GUI: Chat API error for session '{session_id}': {e}", exc_info=True)
        return jsonify({'error': 'Internal server error', 'reply': 'Internal error processing request.'}), 500


# Gunicorn runs 'app' directly
if __name__ == '__main__':
    local_port = int(os.environ.get('PORT', 8081))
    app.run(host='0.0.0.0', port=local_port, debug=True)

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