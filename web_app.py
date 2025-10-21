import streamlit as st
import uuid
import json
from datetime import datetime
import time
import io
import base64

from gemini_chatbot import GeminiChatbot
from config import Config

# Page configuration
st.set_page_config(
    page_title="PGRKAM Digital Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #1e3c72;
    }
    
    .user-message {
        background-color: #e3f2fd;
        margin-left: 20%;
    }
    
    .bot-message {
        background-color: #f5f5f5;
        margin-right: 20%;
    }
    
    .language-selector {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .voice-button {
        background-color: #28a745;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        cursor: pointer;
    }
    
    .job-recommendation {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .sidebar-content {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'selected_language' not in st.session_state:
        st.session_state.selected_language = 'en'
    
    if 'chatbot' not in st.session_state:
        try:
            st.session_state.chatbot = GeminiChatbot()
        except Exception as e:
            st.error(f"Failed to initialize chatbot: {e}")
            st.session_state.chatbot = None
    
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = {
            'preferred_language': 'en',
            'preferred_category': None,
            'experience_level': None,
            'location': None
        }

def display_header():
    """Display the main header"""
    st.markdown("""
    <div class="main-header">
        <h1>🤖 PGRKAM Digital Assistant</h1>
        <p>Your multilingual guide for job search, skill development, and foreign counseling</p>
        <p>Supported Languages: English | हिंदी | ਪੰਜਾਬੀ</p>
    </div>
    """, unsafe_allow_html=True)

def display_language_selector():
    """Display language selection interface"""
    st.markdown('<div class="language-selector">', unsafe_allow_html=True)
    st.subheader("🌐 Language Selection")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("English", key="lang_en"):
            st.session_state.selected_language = 'en'
    
    with col2:
        if st.button("हिंदी", key="lang_hi"):
            st.session_state.selected_language = 'hi'
    
    with col3:
        if st.button("ਪੰਜਾਬੀ", key="lang_pa"):
            st.session_state.selected_language = 'pa'
    
    current_lang = st.session_state.selected_language
    lang_names = {'en': 'English', 'hi': 'हिंदी', 'pa': 'ਪੰਜਾਬੀ'}
    st.info(f"Current Language: {lang_names[current_lang]}")
    st.markdown('</div>', unsafe_allow_html=True)

def display_user_preferences():
    """Display user preferences sidebar"""
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    st.subheader("⚙️ Your Preferences")
    
    # Job Category Preference
    categories = ['Any', 'Government Jobs', 'Private Sector', 'Skill Development', 
                 'Foreign Counseling', 'Education', 'Healthcare', 'Technology']
    
    selected_category = st.selectbox(
        "Preferred Job Category",
        categories,
        index=categories.index(st.session_state.user_preferences.get('preferred_category', 'Any'))
    )
    
    if selected_category != 'Any':
        st.session_state.user_preferences['preferred_category'] = selected_category
    else:
        st.session_state.user_preferences['preferred_category'] = None
    
    # Experience Level
    experience_levels = ['Any', 'Entry Level (0-2 years)', 'Mid Level (2-5 years)', 
                        'Senior Level (5+ years)']
    
    selected_experience = st.selectbox(
        "Experience Level",
        experience_levels,
        index=experience_levels.index(st.session_state.user_preferences.get('experience_level', 'Any'))
    )
    
    if selected_experience != 'Any':
        st.session_state.user_preferences['experience_level'] = selected_experience
    else:
        st.session_state.user_preferences['experience_level'] = None
    
    # Location Preference
    location = st.text_input("Preferred Location", 
                            value=st.session_state.user_preferences.get('location', ''))
    st.session_state.user_preferences['location'] = location
    
    # Save preferences
    if st.button("💾 Save Preferences"):
        if st.session_state.chatbot:
            st.session_state.chatbot.update_user_preferences(
                st.session_state.session_id, 
                st.session_state.user_preferences
            )
            st.success("Preferences saved successfully!")
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_chat_interface():
    """Display the main chat interface"""
    st.subheader("💬 Chat with PGRKAM Assistant")
    
    # Input methods
    input_method = st.radio(
        "Choose input method:",
        ["Text Input", "Voice Input"],
        horizontal=True
    )
    
    user_input = ""
    
    if input_method == "Text Input":
        user_input = st.text_area(
            "Type your question here:",
            placeholder="Ask about jobs, skill development, or foreign counseling...",
            height=100
        )
    else:
        st.markdown("### 🎤 Voice Input")
        if st.button("🎤 Start Recording", key="voice_btn"):
            with st.spinner("Listening... Speak now!"):
                if st.session_state.chatbot:
                    user_input = st.session_state.chatbot.process_voice_input(
                        st.session_state.selected_language
                    )
                    if user_input and "failed" not in user_input.lower():
                        st.success(f"Voice input: {user_input}")
                    else:
                        st.error("Voice recognition failed. Please try again.")
    
    # Process input
    if st.button("🚀 Send", disabled=not user_input.strip()):
        if st.session_state.chatbot and user_input.strip():
            with st.spinner("Processing your request..."):
                # Process the query
                result = st.session_state.chatbot.process_query(
                    user_input,
                    st.session_state.session_id,
                    st.session_state.selected_language,
                    'voice' if input_method == "Voice Input" else 'text'
                )
                
                # Add to chat history
                st.session_state.chat_history.append({
                    'type': 'user',
                    'content': user_input,
                    'language': st.session_state.selected_language,
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                })
                
                st.session_state.chat_history.append({
                    'type': 'bot',
                    'content': result['response'],
                    'language': result['language'],
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                })
                
                # Speak the response
                if input_method == "Voice Input":
                    st.session_state.chatbot.speak_text(result['response'])

def display_chat_history():
    """Display chat history"""
    if st.session_state.chat_history:
        st.subheader("📜 Chat History")
        
        for message in reversed(st.session_state.chat_history[-10:]):  # Show last 10 messages
            if message['type'] == 'user':
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You ({message['timestamp']}):</strong><br>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message bot-message">
                    <strong>Assistant ({message['timestamp']}):</strong><br>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No chat history yet. Start a conversation!")

def display_quick_actions():
    """Display quick action buttons"""
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 Find Jobs"):
            if st.session_state.chatbot:
                result = st.session_state.chatbot.process_query(
                    "Show me available jobs",
                    st.session_state.session_id,
                    st.session_state.selected_language
                )
                st.session_state.chat_history.append({
                    'type': 'user',
                    'content': 'Show me available jobs',
                    'language': st.session_state.selected_language,
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                })
                st.session_state.chat_history.append({
                    'type': 'bot',
                    'content': result['response'],
                    'language': result['language'],
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                })
    
    with col2:
        if st.button("🎓 Skill Development"):
            if st.session_state.chatbot:
                result = st.session_state.chatbot.process_query(
                    "Tell me about skill development programs",
                    st.session_state.session_id,
                    st.session_state.selected_language
                )
                st.session_state.chat_history.append({
                    'type': 'user',
                    'content': 'Tell me about skill development programs',
                    'language': st.session_state.selected_language,
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                })
                st.session_state.chat_history.append({
                    'type': 'bot',
                    'content': result['response'],
                    'language': result['language'],
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                })
    
    with col3:
        if st.button("🌍 Foreign Counseling"):
            if st.session_state.chatbot:
                result = st.session_state.chatbot.process_query(
                    "Tell me about foreign counseling services",
                    st.session_state.session_id,
                    st.session_state.selected_language
                )
                st.session_state.chat_history.append({
                    'type': 'user',
                    'content': 'Tell me about foreign counseling services',
                    'language': st.session_state.selected_language,
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                })
                st.session_state.chat_history.append({
                    'type': 'bot',
                    'content': result['response'],
                    'language': result['language'],
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                })

def display_footer():
    """Display footer information"""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p><strong>PGRKAM Digital Assistant</strong> - Powered by AI</p>
        <p>Your gateway to opportunities in Punjab Government Recruitment and Knowledge Acquisition Mission</p>
        <p>For support, contact: support@pgrkam.gov.in</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application function"""
    initialize_session_state()
    
    # Display header
    display_header()
    
    # Create main layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Language selection
        display_language_selector()
        
        # Quick actions
        display_quick_actions()
        
        # Chat interface
        display_chat_interface()
        
        # Chat history
        display_chat_history()
    
    with col2:
        # User preferences sidebar
        display_user_preferences()
        
        # Session info
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.subheader("ℹ️ Session Info")
        st.write(f"Session ID: {st.session_state.session_id[:8]}...")
        st.write(f"Language: {st.session_state.selected_language}")
        st.write(f"Messages: {len(st.session_state.chat_history)}")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.success("Chat history cleared!")
        
        # Export chat button
        if st.button("📥 Export Chat"):
            if st.session_state.chat_history:
                chat_data = {
                    'session_id': st.session_state.session_id,
                    'exported_at': datetime.now().isoformat(),
                    'chat_history': st.session_state.chat_history
                }
                
                json_str = json.dumps(chat_data, indent=2, ensure_ascii=False)
                st.download_button(
                    label="Download Chat History",
                    data=json_str,
                    file_name=f"pgrkam_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            else:
                st.warning("No chat history to export")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display footer
    display_footer()

if __name__ == "__main__":
    main()
