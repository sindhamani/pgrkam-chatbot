from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import logging
from datetime import datetime

from gemini_chatbot import GeminiChatbot
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize chatbot
try:
    chatbot = GeminiChatbot()
    logger.info("Chatbot initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize chatbot: {e}")
    chatbot = None

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PGRKAM Digital Assistant</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
        }
        .chat-container {
            height: 400px;
            overflow-y: auto;
            padding: 20px;
            border-bottom: 1px solid #eee;
        }
        .message {
            margin: 15px 0;
            padding: 15px;
            border-radius: 10px;
            max-width: 80%;
        }
        .user-message {
            background: #e3f2fd;
            margin-left: auto;
            text-align: right;
        }
        .bot-message {
            background: #f5f5f5;
            margin-right: auto;
        }
        .input-container {
            padding: 20px;
            display: flex;
            gap: 10px;
        }
        .input-container input {
            flex: 1;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
        }
        .input-container input:focus {
            border-color: #1e3c72;
        }
        .input-container button {
            padding: 15px 30px;
            background: #1e3c72;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.3s;
        }
        .input-container button:hover {
            background: #2a5298;
        }
        .language-selector {
            padding: 20px;
            background: #f8f9fa;
            border-top: 1px solid #eee;
        }
        .lang-btn {
            padding: 10px 20px;
            margin: 5px;
            border: 2px solid #1e3c72;
            background: white;
            color: #1e3c72;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .lang-btn.active {
            background: #1e3c72;
            color: white;
        }
        .loading {
            text-align: center;
            color: #666;
            font-style: italic;
        }
        .error {
            color: #d32f2f;
            background: #ffebee;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 PGRKAM Digital Assistant</h1>
            <p>Your multilingual guide for job search, skill development, and foreign counseling</p>
        </div>
        
        <div class="chat-container" id="chatContainer">
            <div class="bot-message">
                Welcome to PGRKAM Digital Assistant! I can help you with job search, skill development, and foreign counseling in English, Hindi, or Punjabi. How can I assist you today?
            </div>
        </div>
        
        <div class="input-container">
            <input type="text" id="userInput" placeholder="Type your question here..." onkeypress="handleKeyPress(event)">
            <button onclick="sendMessage()">Send</button>
        </div>
        
        <div class="language-selector">
            <span>Language: </span>
            <button class="lang-btn active" onclick="setLanguage('en')">English</button>
            <button class="lang-btn" onclick="setLanguage('hi')">हिंदी</button>
            <button class="lang-btn" onclick="setLanguage('pa')">ਪੰਜਾਬੀ</button>
        </div>
    </div>

    <script>
        let currentLanguage = 'en';
        let sessionId = 'session_' + Date.now();

        function setLanguage(lang) {
            currentLanguage = lang;
            document.querySelectorAll('.lang-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        async function sendMessage() {
            const input = document.getElementById('userInput');
            const message = input.value.trim();
            
            if (!message) return;

            // Add user message to chat
            addMessage(message, 'user');
            input.value = '';

            // Show loading
            const loadingDiv = addMessage('Thinking...', 'bot', true);
            loadingDiv.classList.add('loading');

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        query: message,
                        language: currentLanguage,
                        session_id: sessionId
                    })
                });

                const data = await response.json();
                
                // Remove loading message
                loadingDiv.remove();

                if (data.response) {
                    addMessage(data.response, 'bot');
                } else {
                    addMessage('Sorry, I encountered an error. Please try again.', 'bot');
                }
            } catch (error) {
                loadingDiv.remove();
                addMessage('Connection error. Please check your internet connection.', 'bot');
                console.error('Error:', error);
            }
        }

        function addMessage(text, sender, isLoading = false) {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            messageDiv.textContent = text;
            
            if (isLoading) {
                messageDiv.id = 'loading-message';
            }
            
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            
            return messageDiv;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'chatbot_available': chatbot is not None
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests"""
    try:
        if not chatbot:
            return jsonify({
                'error': 'Chatbot not available',
                'response': 'Service temporarily unavailable. Please try again later.'
            }), 500

        data = request.get_json()
        query = data.get('query', '').strip()
        language = data.get('language', 'en')
        session_id = data.get('session_id', 'default')
        input_type = data.get('input_type', 'text')

        if not query:
            return jsonify({
                'error': 'Empty query',
                'response': 'Please provide a question.'
            }), 400

        # Process the query
        result = chatbot.process_query(query, session_id, language, input_type)
        
        return jsonify(result)

    except Exception as e:
        logger.error(f"Chat API error: {e}")
        return jsonify({
            'error': str(e),
            'response': 'I apologize, but I encountered an error processing your request.'
        }), 500

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    """Get job recommendations"""
    try:
        if not chatbot:
            return jsonify({'error': 'Chatbot not available'}), 500

        session_id = request.args.get('session_id', 'default')
        category = request.args.get('category')
        
        # Get recommendations
        recommendations = chatbot.recommend_jobs(session_id, f"Find jobs in {category}" if category else "Find jobs")
        
        return jsonify({
            'recommendations': recommendations,
            'session_id': session_id
        })

    except Exception as e:
        logger.error(f"Recommendations API error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/preferences', methods=['GET', 'PUT'])
def handle_preferences():
    """Handle user preferences"""
    try:
        if not chatbot:
            return jsonify({'error': 'Chatbot not available'}), 500

        session_id = request.args.get('session_id') or request.json.get('session_id')
        
        if request.method == 'GET':
            preferences = chatbot.get_user_preferences(session_id)
            return jsonify({'preferences': preferences})
        
        elif request.method == 'PUT':
            data = request.get_json()
            preferences = data.get('preferences', {})
            chatbot.update_user_preferences(session_id, preferences)
            return jsonify({'message': 'Preferences updated successfully'})

    except Exception as e:
        logger.error(f"Preferences API error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get conversation history"""
    try:
        if not chatbot:
            return jsonify({'error': 'Chatbot not available'}), 500

        session_id = request.args.get('session_id', 'default')
        limit = int(request.args.get('limit', 10))
        
        history = chatbot.get_conversation_history(session_id, limit)
        
        return jsonify({
            'history': history,
            'session_id': session_id
        })

    except Exception as e:
        logger.error(f"History API error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
