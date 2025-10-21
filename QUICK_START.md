# 🚀 Quick Start Guide - PGRKAM Digital Assistant

## 📋 What You'll Get

A complete multilingual chatbot system with:
- ✅ **Multilingual Support**: English, Hindi (हिंदी), Punjabi (ਪੰਜਾਬੀ)
- ✅ **Voice Input/Output**: Speak and listen to responses
- ✅ **Job Recommendations**: Smart job matching based on preferences
- ✅ **User History**: Personalized conversation tracking
- ✅ **Web Interface**: Beautiful UI for smartphones and laptops
- ✅ **Accessibility**: Screen reading and keyboard navigation
- ✅ **RAG System**: Enhanced responses using document search

## 🛠️ Step-by-Step Setup

### Step 1: Prerequisites Check
```bash
# Check Python version (need 3.8+)
python --version

# If Python not installed, download from python.org
```

### Step 2: Get API Keys
1. **Google Gemini API Key**: 
   - Go to https://makersuite.google.com/app/apikey
   - Create account and generate API key
   - Copy the key

2. **Google Cloud Account** (Optional for cloud deployment):
   - Go to https://cloud.google.com
   - Create free account
   - Get project ID from console

### Step 3: Install Dependencies
```bash
# Navigate to project folder
cd Chat-Application-Using-RAG-dev2

# Install all required packages
pip install -r requirement.txt

# If you encounter issues, try:
pip install --upgrade pip
pip install -r requirement.txt --no-cache-dir
```

### Step 4: Configure Environment
Create a `.env` file in the project folder:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
```

**Replace `your_gemini_api_key_here` with your actual Gemini API key**

### Step 5: Test Installation
```bash
# Run the test script
python test_installation.py
```

### Step 6: Run the Application

#### Option A: Web Interface (Recommended)
```bash
streamlit run web_app.py
```
- Open browser to `http://localhost:8501`
- Choose your language
- Start chatting!

#### Option B: Command Line Interface
```bash
python multilingual_chatbot.py
```

#### Option C: Gemini-Powered CLI
```bash
python gemini_chatbot.py
```

## 🎯 How to Use

### Web Interface Features
1. **Language Selection**: Click English/Hindi/ਪੰਜਾਬੀ buttons
2. **Text Input**: Type questions in the text area
3. **Voice Input**: Click microphone button and speak
4. **Quick Actions**: Use preset buttons for common queries
5. **Preferences**: Set job preferences in sidebar
6. **History**: View past conversations

### Example Queries
```
English:
- "Find government jobs in Punjab"
- "Tell me about skill development programs"
- "I need help with foreign counseling"

Hindi:
- "पंजाब में सरकारी नौकरियां खोजें"
- "कौशल विकास कार्यक्रमों के बारे में बताएं"

Punjabi:
- "ਪੰਜਾਬ ਵਿੱਚ ਸਰਕਾਰੀ ਨੌਕਰੀਆਂ ਲੱਭੋ"
- "ਹੁਨਰ ਵਿਕਾਸ ਪ੍ਰੋਗਰਾਮਾਂ ਬਾਰੇ ਦੱਸੋ"
```

### Voice Commands
- Click microphone button
- Speak clearly in your chosen language
- Wait for processing
- Listen to the response

## 🔧 Troubleshooting

### Common Issues & Solutions

#### 1. "No module named 'google.generativeai'"
```bash
pip install google-generativeai
```

#### 2. Voice not working
- Check microphone permissions
- Install audio drivers
- Try different microphone

#### 3. API errors
- Verify Gemini API key in `.env` file
- Check internet connection
- Ensure sufficient API quotas

#### 4. Database errors
```bash
# Delete and recreate database
rm chatbot.db
python gemini_chatbot.py
```

#### 5. Web interface not loading
```bash
# Check if port 8501 is free
streamlit run web_app.py --server.port 8502
```

### Getting Help
1. Check the console output for error messages
2. Run `python test_installation.py` for diagnostics
3. Read the full README.md for detailed documentation
4. Check API key configuration in `.env` file

## 🎉 Success Indicators

You'll know it's working when:
- ✅ Web interface loads without errors
- ✅ You can type and receive responses
- ✅ Language switching works
- ✅ Voice input/output functions
- ✅ Job recommendations appear
- ✅ Conversation history is saved
- ✅ Gemini API integration working

## 📱 Mobile Usage

The web interface is mobile-responsive:
1. Open browser on your phone
2. Go to the same URL (e.g., `http://your-computer-ip:8501`)
3. Use voice input for easier mobile interaction
4. Swipe to navigate between sections

## 🔒 Security Notes

- Keep your Gemini API key secure
- Don't share your `.env` file
- Conversations are stored locally (or in Firestore for cloud deployment)
- Voice data is not permanently saved

## 📞 Support

If you encounter issues:
1. Check this Quick Start guide first
2. Run the test script for diagnostics
3. Check the main README.md
4. Verify all dependencies are installed
5. Ensure API keys are correctly configured

---

**Ready to start? Run `streamlit run web_app.py` and begin your conversation with the PGRKAM Digital Assistant!**

## ☁️ Google Cloud Deployment

For production deployment on Google Cloud:

1. **Setup Cloud Resources**: `./setup_cloud.sh`
2. **Deploy Application**: `./deploy.sh`
3. **Access**: Your app will be available at the provided Cloud Run URL

See [GOOGLE_CLOUD_DEPLOYMENT.md](GOOGLE_CLOUD_DEPLOYMENT.md) for detailed instructions.

**🚀 Ready to start? Run `streamlit run web_app.py` and begin your conversation with the PGRKAM Digital Assistant!**
