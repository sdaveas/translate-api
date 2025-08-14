"""
Simple test script for the Translation Manager.
"""

from translation_manager import TranslationManager

def test_translations():
    """Test basic translations between Chinese, English, and Greek."""
    
    print("Initializing Translation Manager...")
    manager = TranslationManager("translation_config.json")
    
    # Test Chinese to Greek (chain translation)
    print("\n" + "="*60)
    print("TEST: Chinese → Greek (via English)")
    print("="*60)
    
    chinese_text = "你好，世界！今天天气很好。"
    print(f"Original Chinese: {chinese_text}")
    
    greek_result = manager.translate(chinese_text, "zh", "el")
    print(f"Greek translation: {greek_result}")
    
    # Test Greek back to Chinese (chain translation)
    print("\n" + "="*60)
    print("TEST: Greek → Chinese (via English)")
    print("="*60)
    
    greek_text = "Καλημέρα κόσμε! Πώς είσαι σήμερα;"
    print(f"Original Greek: {greek_text}")
    
    chinese_result = manager.translate(greek_text, "el", "zh")
    print(f"Chinese translation: {chinese_result}")
    
    # Test English to both
    print("\n" + "="*60)
    print("TEST: English → Greek and Chinese")
    print("="*60)
    
    english_text = "Hello world! How are you today?"
    print(f"Original English: {english_text}")
    
    greek_from_en = manager.translate(english_text, "en", "el")
    print(f"Greek translation: {greek_from_en}")
    
    chinese_from_en = manager.translate(english_text, "en", "zh")
    print(f"Chinese translation: {chinese_from_en}")
    
    print("\n" + "="*60)
    print("All tests completed successfully!")
    print("="*60)

if __name__ == "__main__":
    test_translations()
