import pyautogui
import pyperclip
import time
import threading
from typing import Optional, Callable
import logging

from multilingual_chatbot import MultilingualChatbot
from config import Config

logger = logging.getLogger(__name__)

class ScreenReader:
    """Accessibility module for screen reading functionality"""
    
    def __init__(self, chatbot: Optional[MultilingualChatbot] = None):
        self.config = Config()
        self.chatbot = chatbot
        self.is_reading = False
        self.reading_thread = None
        self.stop_reading = False
        
        # Configure pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
    def read_selected_text(self, language: str = 'en') -> str:
        """Read the currently selected text using clipboard"""
        try:
            # Save current clipboard content
            original_clipboard = pyperclip.paste()
            
            # Copy selected text
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.5)  # Wait for copy operation
            
            # Get copied text
            selected_text = pyperclip.paste()
            
            # Restore original clipboard
            pyperclip.copy(original_clipboard)
            
            if selected_text and selected_text != original_clipboard:
                logger.info(f"Read selected text: {selected_text[:100]}...")
                return selected_text
            else:
                return ""
                
        except Exception as e:
            logger.error(f"Error reading selected text: {e}")
            return ""
    
    def read_screen_region(self, x: int, y: int, width: int, height: int, 
                          language: str = 'en') -> str:
        """Read text from a specific screen region using OCR"""
        try:
            # Take screenshot of the region
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            
            # For now, we'll use a simple approach
            # In a real implementation, you would use OCR libraries like pytesseract
            # or cloud OCR services
            
            # Placeholder for OCR functionality
            # This would require additional dependencies like pytesseract
            logger.info(f"Screenshot taken of region: {x}, {y}, {width}, {height}")
            
            return "Screen region reading requires OCR setup. Please install pytesseract for full functionality."
            
        except Exception as e:
            logger.error(f"Error reading screen region: {e}")
            return ""
    
    def speak_text(self, text: str, language: str = 'en'):
        """Convert text to speech for accessibility"""
        if self.chatbot:
            self.chatbot.speak_text(text)
        else:
            logger.warning("Chatbot not available for text-to-speech")
    
    def start_continuous_reading(self, language: str = 'en', 
                                interval: int = 5, 
                                callback: Optional[Callable] = None):
        """Start continuous screen reading"""
        if self.is_reading:
            logger.warning("Screen reading already in progress")
            return
        
        self.is_reading = True
        self.stop_reading = False
        
        def reading_loop():
            while self.is_reading and not self.stop_reading:
                try:
                    # Read selected text
                    selected_text = self.read_selected_text(language)
                    
                    if selected_text:
                        # Speak the text
                        self.speak_text(selected_text, language)
                        
                        # Call callback if provided
                        if callback:
                            callback(selected_text)
                    
                    # Wait for next reading
                    time.sleep(interval)
                    
                except Exception as e:
                    logger.error(f"Error in continuous reading: {e}")
                    time.sleep(interval)
        
        self.reading_thread = threading.Thread(target=reading_loop, daemon=True)
        self.reading_thread.start()
        
        logger.info("Continuous screen reading started")
    
    def stop_continuous_reading(self):
        """Stop continuous screen reading"""
        self.is_reading = False
        self.stop_reading = True
        
        if self.reading_thread:
            self.reading_thread.join(timeout=2)
        
        logger.info("Continuous screen reading stopped")
    
    def read_webpage_content(self, url: str = None, language: str = 'en') -> str:
        """Read content from a webpage"""
        try:
            if not url:
                # Try to get current URL from browser
                # This is a simplified approach - in practice, you'd need browser automation
                logger.info("No URL provided, attempting to read current page")
                return "Webpage reading requires browser automation setup"
            
            # In a real implementation, you would use libraries like selenium or requests
            # to fetch and parse webpage content
            
            logger.info(f"Reading webpage: {url}")
            return f"Webpage content from {url} would be read here with proper browser automation"
            
        except Exception as e:
            logger.error(f"Error reading webpage: {e}")
            return ""
    
    def process_screen_content(self, content: str, language: str = 'en') -> str:
        """Process and summarize screen content using the chatbot"""
        if not self.chatbot or not content.strip():
            return ""
        
        try:
            # Create a query for processing screen content
            query = f"Please summarize and explain the following content in {language}: {content}"
            
            result = self.chatbot.process_query(
                query, 
                session_id="screen_reader",
                language=language
            )
            
            return result.get('response', '')
            
        except Exception as e:
            logger.error(f"Error processing screen content: {e}")
            return ""
    
    def accessibility_shortcuts(self):
        """Define accessibility keyboard shortcuts"""
        shortcuts = {
            "Ctrl+Shift+R": "Start/Stop screen reading",
            "Ctrl+Shift+T": "Read selected text",
            "Ctrl+Shift+S": "Speak current screen",
            "Ctrl+Shift+H": "Read help information",
            "Ctrl+Shift+L": "Change language",
            "Ctrl+Shift+P": "Read preferences"
        }
        
        return shortcuts
    
    def get_help_information(self, language: str = 'en') -> str:
        """Get help information for accessibility features"""
        help_text = {
            'en': """
            PGRKAM Digital Assistant - Accessibility Features:
            
            1. Screen Reading: Use Ctrl+Shift+R to start/stop continuous screen reading
            2. Text Selection: Use Ctrl+Shift+T to read currently selected text
            3. Voice Input: Use the voice input feature for hands-free interaction
            4. Language Support: Switch between English, Hindi, and Punjabi
            5. Keyboard Navigation: Use Tab and arrow keys to navigate
            
            For more help, contact support@pgrkam.gov.in
            """,
            'hi': """
            PGRKAM डिजिटल असिस्टेंट - पहुंच योग्यता सुविधाएं:
            
            1. स्क्रीन रीडिंग: निरंतर स्क्रीन रीडिंग शुरू/बंद करने के लिए Ctrl+Shift+R का उपयोग करें
            2. टेक्स्ट चयन: वर्तमान में चयनित टेक्स्ट पढ़ने के लिए Ctrl+Shift+T का उपयोग करें
            3. वॉयस इनपुट: हाथ मुक्त बातचीत के लिए वॉयस इनपुट सुविधा का उपयोग करें
            4. भाषा समर्थन: अंग्रेजी, हिंदी और पंजाबी के बीच स्विच करें
            5. कीबोर्ड नेविगेशन: नेविगेट करने के लिए Tab और एरो की का उपयोग करें
            
            अधिक सहायता के लिए support@pgrkam.gov.in पर संपर्क करें
            """,
            'pa': """
            PGRKAM ਡਿਜੀਟਲ ਅਸਿਸਟੈਂਟ - ਪਹੁੰਚ ਯੋਗਤਾ ਸੁਵਿਧਾਵਾਂ:
            
            1. ਸਕਰੀਨ ਰੀਡਿੰਗ: ਲਗਾਤਾਰ ਸਕਰੀਨ ਰੀਡਿੰਗ ਸ਼ੁਰੂ/ਬੰਦ ਕਰਨ ਲਈ Ctrl+Shift+R ਵਰਤੋਂ
            2. ਟੈਕਸਟ ਚੋਣ: ਮੌਜੂਦਾ ਚੁਣੇ ਗਏ ਟੈਕਸਟ ਪੜ੍ਹਨ ਲਈ Ctrl+Shift+T ਵਰਤੋਂ
            3. ਵੌਇਸ ਇਨਪੁਟ: ਹੱਥ-ਮੁਕਤ ਗੱਲਬਾਤ ਲਈ ਵੌਇਸ ਇਨਪੁਟ ਸੁਵਿਧਾ ਵਰਤੋਂ
            4. ਭਾਸ਼ਾ ਸਹਾਇਤਾ: ਅੰਗਰੇਜ਼ੀ, ਹਿੰਦੀ ਅਤੇ ਪੰਜਾਬੀ ਵਿਚਕਾਰ ਬਦਲੋ
            5. ਕੀਬੋਰਡ ਨੈਵੀਗੇਸ਼ਨ: ਨੈਵੀਗੇਟ ਕਰਨ ਲਈ Tab ਅਤੇ ਐਰੋ ਕੀਜ਼ ਵਰਤੋਂ
            
            ਹੋਰ ਸਹਾਇਤਾ ਲਈ support@pgrkam.gov.in 'ਤੇ ਸੰਪਰਕ ਕਰੋ
            """
        }
        
        return help_text.get(language, help_text['en'])
    
    def setup_accessibility_features(self, language: str = 'en'):
        """Setup accessibility features for the user"""
        try:
            # Speak welcome message
            welcome_message = {
                'en': "Accessibility features are now enabled. Use keyboard shortcuts for screen reading.",
                'hi': "पहुंच योग्यता सुविधाएं अब सक्षम हैं। स्क्रीन रीडिंग के लिए कीबोर्ड शॉर्टकट का उपयोग करें।",
                'pa': "ਪਹੁੰਚ ਯੋਗਤਾ ਸੁਵਿਧਾਵਾਂ ਹੁਣ ਸਮਰੱਥ ਹਨ। ਸਕਰੀਨ ਰੀਡਿੰਗ ਲਈ ਕੀਬੋਰਡ ਸ਼ਾਰਟਕੱਟ ਵਰਤੋਂ।"
            }
            
            message = welcome_message.get(language, welcome_message['en'])
            self.speak_text(message, language)
            
            # Display shortcuts
            shortcuts = self.accessibility_shortcuts()
            print("\nAccessibility Shortcuts:")
            for shortcut, description in shortcuts.items():
                print(f"{shortcut}: {description}")
            
            logger.info("Accessibility features setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up accessibility features: {e}")

class AccessibilityManager:
    """Manager class for accessibility features"""
    
    def __init__(self):
        self.screen_reader = None
        self.chatbot = None
        
    def initialize(self, chatbot: MultilingualChatbot):
        """Initialize accessibility manager with chatbot"""
        self.chatbot = chatbot
        self.screen_reader = ScreenReader(chatbot)
        logger.info("Accessibility manager initialized")
    
    def enable_screen_reading(self, language: str = 'en'):
        """Enable screen reading functionality"""
        if self.screen_reader:
            self.screen_reader.setup_accessibility_features(language)
            return True
        return False
    
    def read_selected_text(self, language: str = 'en') -> str:
        """Read currently selected text"""
        if self.screen_reader:
            return self.screen_reader.read_selected_text(language)
        return ""
    
    def start_continuous_reading(self, language: str = 'en', interval: int = 5):
        """Start continuous screen reading"""
        if self.screen_reader:
            self.screen_reader.start_continuous_reading(language, interval)
            return True
        return False
    
    def stop_continuous_reading(self):
        """Stop continuous screen reading"""
        if self.screen_reader:
            self.screen_reader.stop_continuous_reading()
            return True
        return False
    
    def get_help(self, language: str = 'en') -> str:
        """Get accessibility help information"""
        if self.screen_reader:
            return self.screen_reader.get_help_information(language)
        return "Accessibility features not available"

if __name__ == "__main__":
    # Example usage
    print("PGRKAM Digital Assistant - Accessibility Module")
    print("=" * 50)
    
    # Initialize chatbot and accessibility manager
    try:
        chatbot = MultilingualChatbot()
        accessibility = AccessibilityManager()
        accessibility.initialize(chatbot)
        
        # Enable accessibility features
        accessibility.enable_screen_reading('en')
        
        # Example of reading selected text
        print("\nSelect some text and press Enter to read it...")
        input()
        
        selected_text = accessibility.read_selected_text('en')
        if selected_text:
            print(f"Selected text: {selected_text}")
            chatbot.speak_text(selected_text)
        else:
            print("No text selected or error reading text")
        
        # Display help
        print("\n" + accessibility.get_help('en'))
        
    except Exception as e:
        print(f"Error initializing accessibility features: {e}")
        print("Please ensure all dependencies are installed and API keys are configured.")
