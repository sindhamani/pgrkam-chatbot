#!/usr/bin/env python3
"""
Test script for PGRKAM Digital Assistant
This script tests all major components of the chatbot system.
"""

import sys
import os
import traceback
from datetime import datetime

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing module imports...")
    
    modules_to_test = [
        ('streamlit', 'Web interface framework'),
        ('openai', 'OpenAI API client'),
        ('pinecone', 'Pinecone vector database'),
        ('googletrans', 'Google Translate for multilingual support'),
        ('speech_recognition', 'Speech recognition'),
        ('pyttsx3', 'Text-to-speech'),
        ('sqlite3', 'Database support'),
        ('pandas', 'Data processing'),
        ('requests', 'HTTP requests'),
    ]
    
    failed_imports = []
    
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"   ✅ {module_name} - {description}")
        except ImportError as e:
            print(f"   ❌ {module_name} - {description} (Error: {e})")
            failed_imports.append(module_name)
    
    return len(failed_imports) == 0, failed_imports

def test_config():
    """Test configuration loading"""
    print("\n⚙️  Testing configuration...")
    
    try:
        from config import Config
        config = Config()
        
        print(f"   ✅ Configuration loaded")
        print(f"   📋 App Name: {config.APP_NAME}")
        print(f"   🌐 Supported Languages: {', '.join(config.SUPPORTED_LANGUAGES)}")
        print(f"   📊 Chunk Size: {config.CHUNK_SIZE}")
        
        return True
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")
        return False

def test_translation():
    """Test translation functionality"""
    print("\n🌐 Testing translation...")
    
    try:
        from googletrans import Translator
        translator = Translator()
        
        # Test translation
        test_text = "Hello, how are you?"
        result = translator.translate(test_text, dest='hi')
        
        print(f"   ✅ Translation working")
        print(f"   📝 Original: {test_text}")
        print(f"   🔄 Hindi: {result.text}")
        
        return True
    except Exception as e:
        print(f"   ❌ Translation error: {e}")
        return False

def test_voice_components():
    """Test voice recognition and text-to-speech"""
    print("\n🎤 Testing voice components...")
    
    try:
        import speech_recognition as sr
        import pyttsx3
        
        # Test speech recognition
        recognizer = sr.Recognizer()
        print("   ✅ Speech recognition initialized")
        
        # Test text-to-speech
        tts_engine = pyttsx3.init()
        print("   ✅ Text-to-speech initialized")
        
        return True
    except Exception as e:
        print(f"   ❌ Voice component error: {e}")
        return False

def test_database():
    """Test database functionality"""
    print("\n🗄️  Testing database...")
    
    try:
        import sqlite3
        import json
        
        # Create test database
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        
        # Test table creation
        cursor.execute('''
            CREATE TABLE test_users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                preferences TEXT
            )
        ''')
        
        # Test data insertion
        test_data = {'language': 'en', 'category': 'technology'}
        cursor.execute('''
            INSERT INTO test_users (name, preferences)
            VALUES (?, ?)
        ''', ('Test User', json.dumps(test_data)))
        
        # Test data retrieval
        cursor.execute('SELECT * FROM test_users')
        result = cursor.fetchone()
        
        conn.close()
        
        print("   ✅ Database operations working")
        print(f"   📊 Test data: {result}")
        
        return True
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False

def test_chatbot_initialization():
    """Test chatbot initialization"""
    print("\n🤖 Testing chatbot initialization...")
    
    try:
        # Check if API keys are available
        openai_key = os.getenv('OPENAI_API_KEY', '')
        pinecone_key = os.getenv('PINECONE_API_KEY', '')
        
        if not openai_key or openai_key == 'your_openai_api_key_here':
            print("   ⚠️  OpenAI API key not configured")
            return False
        
        if not pinecone_key or pinecone_key == 'your_pinecone_api_key_here':
            print("   ⚠️  Pinecone API key not configured")
            return False
        
        # Try to import chatbot (this might fail if API keys are invalid)
        try:
            from multilingual_chatbot import MultilingualChatbot
            # Don't actually initialize to avoid API calls during testing
            print("   ✅ Chatbot module imported successfully")
            return True
        except Exception as e:
            print(f"   ❌ Chatbot initialization error: {e}")
            return False
            
    except Exception as e:
        print(f"   ❌ Chatbot test error: {e}")
        return False

def test_web_interface():
    """Test web interface components"""
    print("\n🌐 Testing web interface...")
    
    try:
        import streamlit as st
        print("   ✅ Streamlit available")
        
        # Check if web_app.py exists and is importable
        web_app_path = os.path.join(os.path.dirname(__file__), 'web_app.py')
        if os.path.exists(web_app_path):
            print("   ✅ Web app file exists")
            return True
        else:
            print("   ❌ Web app file not found")
            return False
            
    except Exception as e:
        print(f"   ❌ Web interface error: {e}")
        return False

def test_file_structure():
    """Test if all required files exist"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        'multilingual_chatbot.py',
        'config.py',
        'web_app.py',
        'screen_reader.py',
        'requirement.txt',
        'README.md'
    ]
    
    missing_files = []
    
    for file_name in required_files:
        file_path = os.path.join(os.path.dirname(__file__), file_name)
        if os.path.exists(file_path):
            print(f"   ✅ {file_name}")
        else:
            print(f"   ❌ {file_name} (missing)")
            missing_files.append(file_name)
    
    return len(missing_files) == 0, missing_files

def run_all_tests():
    """Run all tests and provide a summary"""
    print("🚀 PGRKAM Digital Assistant - Installation Test")
    print("=" * 60)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python Version: {sys.version}")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_config),
        ("Translation", test_translation),
        ("Voice Components", test_voice_components),
        ("Database", test_database),
        ("Chatbot Initialization", test_chatbot_initialization),
        ("Web Interface", test_web_interface),
        ("File Structure", test_file_structure),
    ]
    
    results = []
    
    for test_name, test_function in tests:
        try:
            if test_name == "Module Imports":
                success, failed_imports = test_function()
                if not success:
                    print(f"\n⚠️  Failed imports: {', '.join(failed_imports)}")
            elif test_name == "File Structure":
                success, missing_files = test_function()
                if not success:
                    print(f"\n⚠️  Missing files: {', '.join(missing_files)}")
            else:
                success = test_function()
            
            results.append((test_name, success))
            
        except Exception as e:
            print(f"\n❌ Unexpected error in {test_name}: {e}")
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:<25} {status}")
        if success:
            passed += 1
    
    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! The installation is ready to use.")
        print("\n🚀 Next steps:")
        print("1. Run: streamlit run web_app.py")
        print("2. Or run: python multilingual_chatbot.py")
    else:
        print(f"\n⚠️  {total-passed} test(s) failed. Please check the errors above.")
        print("\n🔧 Common solutions:")
        print("- Install missing dependencies: pip install -r requirement.txt")
        print("- Configure API keys in .env file")
        print("- Check file permissions")
        print("- Ensure Python 3.8+ is installed")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
