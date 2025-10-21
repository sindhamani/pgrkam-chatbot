# PGRKAM Digital Assistant - Multilingual Chatbot

A comprehensive multilingual chatbot system built for the Punjab Government Recruitment and Knowledge Acquisition Mission (PGRKAM) platform. This intelligent assistant provides support in English, Hindi, and Punjabi for job search, skill development, and foreign counseling services using Google's Gemini API and Google Cloud services.

## 🌟 Features

### Core Capabilities
- **Multilingual Support**: English, Hindi (हिंदी), and Punjabi (ਪੰਜਾਬੀ)
- **Voice Input/Output**: Speech recognition and text-to-speech
- **RAG (Retrieval Augmented Generation)**: Enhanced responses using vector search
- **User Personalization**: History tracking and preference management
- **Job Recommendations**: Intelligent job matching based on user preferences

### Accessibility Features
- **Screen Reading**: OCR-based screen content reading
- **Keyboard Shortcuts**: Full keyboard navigation support
- **Voice Commands**: Hands-free interaction capabilities
- **Multi-modal Interface**: Text, voice, and visual interaction modes

### Platform Support
- **Web Interface**: Responsive design for smartphones and laptops
- **Desktop Application**: Command-line interface for advanced users
- **API Integration**: RESTful API for third-party integrations

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed on your system
2. **Google Gemini API Key** from https://makersuite.google.com/app/apikey
3. **Google Cloud Account** (optional, for cloud deployment)
4. **Audio Hardware** (microphone and speakers) for voice features

### Installation Steps

1. **Clone or Download** the project files
   ```bash
   cd Chat-Application-Using-RAG-dev2
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirement.txt
   ```

3. **Set Up Environment Variables**
   
   Create a `.env` file in the project directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_CLOUD_LOCATION=us-central1
   ```

4. **Initialize Vector Store** (Optional - for RAG functionality)
   ```bash
   python chatbot.py create-embeddings -s ./documents
   ```

### Running the Application

#### Option 1: Web Interface (Recommended)
```bash
streamlit run web_app.py
```
Open your browser and go to `http://localhost:8501`

#### Option 2: Command Line Interface
```bash
python multilingual_chatbot.py
```

#### Option 3: Gemini-Powered CLI
```bash
python gemini_chatbot.py
```

## 📱 Usage Guide

### Web Interface

1. **Language Selection**: Choose your preferred language (English/Hindi/Punjabi)
2. **Input Methods**:
   - Type your questions in the text area
   - Use voice input by clicking the microphone button
3. **Quick Actions**: Use predefined buttons for common queries
4. **Preferences**: Set your job preferences in the sidebar
5. **Chat History**: View and export your conversation history

### Voice Commands

- **"Find jobs"** - Search for available positions
- **"Skill development"** - Get information about training programs
- **"Foreign counseling"** - Access migration and study abroad services
- **"Change language"** - Switch between supported languages

### Accessibility Features

- **Ctrl+Shift+R**: Start/stop screen reading
- **Ctrl+Shift+T**: Read selected text
- **Ctrl+Shift+S**: Speak current screen content
- **Ctrl+Shift+H**: Display help information

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `GOOGLE_CLOUD_PROJECT` | Google Cloud project ID | Optional |
| `DEFAULT_LANGUAGE` | Default interface language | `en` |
| `SPEECH_RATE` | Text-to-speech speed | `150` |
| `CHUNK_SIZE` | Document chunk size for RAG | `1000` |

### Language Settings

The system supports three languages:
- **English** (`en`): Default language
- **Hindi** (`hi`): Full Unicode support
- **Punjabi** (`pa`): Gurmukhi script support

### Job Categories

- Government Jobs
- Private Sector
- Skill Development
- Foreign Counseling
- Education
- Healthcare
- Technology
- Agriculture
- Banking
- Defense

## 🏗️ Architecture

### System Components

1. **GeminiChatbot**: Core chatbot engine with Gemini API and RAG capabilities
2. **ScreenReader**: Accessibility module for screen reading
3. **WebApp**: Streamlit-based web interface
4. **Database**: SQLite/Firestore for user data and conversation history
5. **Vector Store**: Google Cloud services for document embeddings and similarity search

### Data Flow

```
User Input → Language Detection → Translation (if needed) → 
Vector Search → Gemini API Processing → Response Generation → 
Text-to-Speech → User Output
```

## 📊 Database Schema

### Tables

- **users**: User sessions and preferences
- **conversations**: Chat history and interactions
- **job_preferences**: User job preferences and criteria

### Sample Queries

```sql
-- Get user preferences
SELECT preferences FROM users WHERE session_id = ?;

-- Get conversation history
SELECT * FROM conversations WHERE session_id = ? ORDER BY timestamp DESC;

-- Update job preferences
INSERT OR REPLACE INTO job_preferences (session_id, category, keywords) 
VALUES (?, ?, ?);
```

## 🔌 API Integration

### RESTful Endpoints

```python
# Process query
POST /api/chat
{
    "query": "Find government jobs",
    "language": "en",
    "session_id": "user123"
}

# Get recommendations
GET /api/recommendations?session_id=user123&category=government

# Update preferences
PUT /api/preferences
{
    "session_id": "user123",
    "preferences": {
        "language": "hi",
        "category": "technology"
    }
}
```

## 🧪 Testing

### Unit Tests
```bash
python -m pytest tests/
```

### Integration Tests
```bash
python test_integration.py
```

### Manual Testing
1. Test voice input/output with different languages
2. Verify job recommendation accuracy
3. Check accessibility features
4. Test web interface responsiveness

## 🚨 Troubleshooting

### Common Issues

1. **Voice Recognition Not Working**
   - Check microphone permissions
   - Ensure audio drivers are installed
   - Try different language settings

2. **API Errors**
   - Verify API keys in `.env` file
   - Check internet connectivity
   - Ensure sufficient API credits

3. **Database Issues**
   - Check file permissions for `chatbot.db`
   - Verify SQLite installation
   - Clear database if corrupted

4. **Translation Issues**
   - Check internet connection for Google Translate
   - Verify language codes are correct
   - Try alternative translation services

### Error Logs

Check the console output for detailed error messages. Logs are also saved to:
- `chatbot.log` - Main application logs
- `accessibility.log` - Screen reader logs
- `web_app.log` - Web interface logs

## 🔒 Security Considerations

- **API Keys**: Never commit API keys to version control
- **User Data**: All conversations are stored locally in SQLite
- **Audio Data**: Voice recordings are not stored permanently
- **Privacy**: User preferences are encrypted in the database

## 🌐 Deployment

### Local Deployment
```bash
# Development server
streamlit run web_app.py --server.port 8501

# Production server
gunicorn -w 4 -b 0.0.0.0:8000 flask_app:app
```

### Google Cloud Deployment (Recommended)

1. **Quick Setup**: Run `./setup_cloud.sh`
2. **Deploy**: Run `./deploy.sh`
3. **Access**: Your app will be available at the provided Cloud Run URL

For detailed instructions, see [GOOGLE_CLOUD_DEPLOYMENT.md](GOOGLE_CLOUD_DEPLOYMENT.md)

### Other Cloud Platforms

1. **AWS**: Deploy using EC2 or Lambda
2. **Azure**: Deploy using App Service
3. **Heroku**: Use Procfile for deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirement.txt
EXPOSE 8501
CMD ["streamlit", "run", "web_app.py"]
```

## 📈 Performance Optimization

### Recommendations

1. **Vector Store**: Use Pinecone for fast similarity search
2. **Caching**: Implement response caching for common queries
3. **CDN**: Use content delivery network for static assets
4. **Database**: Index frequently queried columns
5. **Audio**: Compress audio files for faster transmission

### Monitoring

- **Response Time**: Monitor average response time
- **API Usage**: Track OpenAI and Pinecone API calls
- **User Engagement**: Analyze conversation patterns
- **Error Rates**: Monitor and alert on high error rates

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Use type hints for function parameters
- Add docstrings for all functions
- Include error handling for external API calls

## 📞 Support

### Contact Information

- **Email**: support@pgrkam.gov.in
- **Phone**: +91-XXX-XXXX-XXXX
- **Website**: https://pgrkam.gov.in

### Documentation

- **API Documentation**: `/docs/api.md`
- **User Guide**: `/docs/user_guide.md`
- **Developer Guide**: `/docs/developer_guide.md`

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google for Gemini API and Cloud services
- Google Translate for multilingual support
- Streamlit for web interface framework
- Punjab Government for the PGRKAM initiative

---

**Version**: 1.0.0  
**Last Updated**: December 2024  
**Maintainer**: PGRKAM Development Team
