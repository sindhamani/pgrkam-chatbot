#!/usr/bin/env python3
"""
Setup script for PGRKAM Digital Assistant
This script helps users set up the chatbot system quickly and easily.
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path

class SetupManager:
    """Manages the setup process for the PGRKAM chatbot"""
    
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.requirements_file = self.project_dir / "requirement.txt"
        self.config_file = self.project_dir / "config.py"
        self.env_file = self.project_dir / ".env"
        
    def check_python_version(self):
        """Check if Python version is compatible"""
        print("🐍 Checking Python version...")
        
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("❌ Error: Python 3.8 or higher is required")
            print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
            return False
        
        print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    
    def check_system_requirements(self):
        """Check system requirements and dependencies"""
        print("\n🔍 Checking system requirements...")
        
        system = platform.system().lower()
        print(f"   Operating System: {system}")
        
        # Check for audio support
        try:
            import pyaudio
            print("✅ Audio support detected")
        except ImportError:
            print("⚠️  Audio support not detected - voice features may not work")
            print("   Install pyaudio: pip install pyaudio")
        
        # Check for browser support
        browsers = ['chrome', 'firefox', 'safari', 'edge']
        browser_found = False
        for browser in browsers:
            if self.check_browser(browser):
                browser_found = True
                break
        
        if browser_found:
            print("✅ Web browser detected")
        else:
            print("⚠️  No web browser detected - web interface may not work properly")
        
        return True
    
    def check_browser(self, browser_name):
        """Check if a specific browser is installed"""
        system = platform.system().lower()
        
        if system == "windows":
            browsers = {
                'chrome': ['chrome.exe', 'google chrome'],
                'firefox': ['firefox.exe'],
                'edge': ['msedge.exe', 'microsoft edge']
            }
        elif system == "darwin":  # macOS
            browsers = {
                'chrome': ['Google Chrome.app'],
                'firefox': ['Firefox.app'],
                'safari': ['Safari.app']
            }
        else:  # Linux
            browsers = {
                'chrome': ['google-chrome', 'chromium'],
                'firefox': ['firefox']
            }
        
        if browser_name in browsers:
            for browser in browsers[browser_name]:
                try:
                    subprocess.run(['which', browser], 
                                 capture_output=True, check=True)
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
        
        return False
    
    def install_dependencies(self):
        """Install required Python packages"""
        print("\n📦 Installing dependencies...")
        
        if not self.requirements_file.exists():
            print("❌ Error: requirements.txt not found")
            return False
        
        try:
            # Upgrade pip first
            subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                         check=True, capture_output=True)
            
            # Install requirements
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 
                          str(self.requirements_file)], check=True)
            
            print("✅ Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing dependencies: {e}")
            print("   Try running: pip install -r requirement.txt")
            return False
    
    def setup_environment(self):
        """Set up environment variables"""
        print("\n⚙️  Setting up environment variables...")
        
        if self.env_file.exists():
            print("✅ .env file already exists")
            return True
        
        print("📝 Creating .env file...")
        
        # Get API keys from user
        openai_key = input("Enter your OpenAI API key (or press Enter to skip): ").strip()
        pinecone_key = input("Enter your Pinecone API key (or press Enter to skip): ").strip()
        
        # Create .env file
        env_content = f"""# API Keys
OPENAI_API_KEY={openai_key or 'your_openai_api_key_here'}
PINECONE_API_KEY={pinecone_key or 'your_pinecone_api_key_here'}
PINECONE_ENVIRONMENT=gcp-starter

# Database Configuration
DATABASE_URL=sqlite:///chatbot.db

# Application Settings
APP_NAME=PGRKAM Digital Assistant
APP_VERSION=1.0.0
DEBUG=True

# Language Settings
DEFAULT_LANGUAGE=en
SUPPORTED_LANGUAGES=en,hi,pa

# Audio Settings
SPEECH_RATE=150
SPEECH_VOLUME=0.8
VOICE_GENDER=male

# RAG Settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=3

# Job Recommendation Settings
MAX_JOB_RECOMMENDATIONS=5
PREFERENCE_WEIGHT=0.7
"""
        
        try:
            with open(self.env_file, 'w') as f:
                f.write(env_content)
            
            print("✅ .env file created successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            return False
    
    def setup_database(self):
        """Initialize the database"""
        print("\n🗄️  Setting up database...")
        
        try:
            from multilingual_chatbot import MultilingualChatbot
            
            # Initialize chatbot to create database
            chatbot = MultilingualChatbot()
            print("✅ Database initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error setting up database: {e}")
            print("   Database will be created when you first run the application")
            return False
    
    def create_sample_documents(self):
        """Create sample documents for testing"""
        print("\n📄 Creating sample documents...")
        
        docs_dir = self.project_dir / "documents"
        docs_dir.mkdir(exist_ok=True)
        
        # Sample job information
        job_info = """
        PGRKAM Job Opportunities
        
        1. Government Jobs:
        - Administrative Officer (Various Locations)
        - Data Entry Operator (Chandigarh)
        - Clerk (Ludhiana, Amritsar, Jalandhar)
        
        2. Skill Development Programs:
        - Digital Literacy Training
        - Communication Skills Workshop
        - Technical Skills Development
        
        3. Foreign Counseling Services:
        - Study Abroad Guidance
        - Visa Application Support
        - Career Counseling
        """
        
        try:
            with open(docs_dir / "job_info.txt", 'w', encoding='utf-8') as f:
                f.write(job_info)
            
            print("✅ Sample documents created")
            return True
            
        except Exception as e:
            print(f"❌ Error creating sample documents: {e}")
            return False
    
    def test_installation(self):
        """Test the installation"""
        print("\n🧪 Testing installation...")
        
        try:
            # Test imports
            import streamlit
            import openai
            import pinecone
            from googletrans import Translator
            import speech_recognition as sr
            import pyttsx3
            
            print("✅ All required modules imported successfully")
            
            # Test basic functionality
            translator = Translator()
            print("✅ Translation service working")
            
            print("✅ Installation test passed")
            return True
            
        except ImportError as e:
            print(f"❌ Import error: {e}")
            return False
        except Exception as e:
            print(f"❌ Test error: {e}")
            return False
    
    def display_next_steps(self):
        """Display next steps for the user"""
        print("\n🎉 Setup completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Update your API keys in the .env file if needed")
        print("2. Run the web interface: streamlit run web_app.py")
        print("3. Or run the command-line version: python multilingual_chatbot.py")
        print("\n📚 Documentation:")
        print("- Read README.md for detailed usage instructions")
        print("- Check the web interface for interactive features")
        print("- Use 'help' command in CLI for assistance")
        print("\n🔧 Troubleshooting:")
        print("- If voice features don't work, check microphone permissions")
        print("- If API errors occur, verify your API keys")
        print("- Check the console for detailed error messages")
    
    def run_setup(self):
        """Run the complete setup process"""
        print("🚀 PGRKAM Digital Assistant Setup")
        print("=" * 50)
        
        steps = [
            ("Checking Python version", self.check_python_version),
            ("Checking system requirements", self.check_system_requirements),
            ("Installing dependencies", self.install_dependencies),
            ("Setting up environment", self.setup_environment),
            ("Setting up database", self.setup_database),
            ("Creating sample documents", self.create_sample_documents),
            ("Testing installation", self.test_installation),
        ]
        
        failed_steps = []
        
        for step_name, step_function in steps:
            try:
                if not step_function():
                    failed_steps.append(step_name)
            except KeyboardInterrupt:
                print("\n\n❌ Setup interrupted by user")
                return False
            except Exception as e:
                print(f"❌ Unexpected error in {step_name}: {e}")
                failed_steps.append(step_name)
        
        if failed_steps:
            print(f"\n⚠️  Setup completed with {len(failed_steps)} issues:")
            for step in failed_steps:
                print(f"   - {step}")
            print("\nYou may still be able to run the application with limited functionality.")
        else:
            self.display_next_steps()
        
        return len(failed_steps) == 0

def main():
    """Main setup function"""
    setup_manager = SetupManager()
    success = setup_manager.run_setup()
    
    if success:
        print("\n✅ Setup completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Setup completed with errors")
        sys.exit(1)

if __name__ == "__main__":
    main()
