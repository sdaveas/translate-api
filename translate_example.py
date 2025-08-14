"""
Example usage of the Translation Manager for Chinese, English, and Greek translations.
"""

from translation_manager import TranslationManager
import logging

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def main():
    # Initialize the translation manager
    print("="*60)
    print("Translation Manager Example")
    print("="*60)
    
    manager = TranslationManager("translation_config.json")
    
    # Show available translation routes
    print("\nAvailable translation routes:")
    routes = manager.get_available_routes()
    for source, targets in routes.items():
        print(f"  From {source} to: {', '.join(targets)}")
    
    print("\n" + "="*60)
    
    # Example texts in different languages
    test_texts = {
        "zh": "你好世界！今天天气很好。我喜欢学习新语言。",
        "en": "Hello world! The weather is nice today. I love learning new languages.",
        "el": "Γεια σου κόσμε! Ο καιρός είναι ωραίος σήμερα. Μου αρέσει να μαθαίνω νέες γλώσσες."
    }
    
    # Test translations between all language pairs
    test_cases = [
        # Direct translations
        ("zh", "en", "Chinese to English (direct)"),
        ("en", "zh", "English to Chinese (direct)"),
        ("en", "el", "English to Greek (direct)"),
        ("el", "en", "Greek to English (direct)"),
        
        # Chain translations
        ("zh", "el", "Chinese to Greek (via English)"),
        ("el", "zh", "Greek to Chinese (via English)"),
    ]
    
    for source_lang, target_lang, description in test_cases:
        print(f"\n{description}:")
        print("-" * 40)
        
        source_text = test_texts.get(source_lang)
        if not source_text:
            print(f"No test text available for {source_lang}")
            continue
        
        print(f"Original ({manager.config['language_names'][source_lang]}):")
        print(f"  {source_text}")
        
        try:
            # Perform translation
            translated = manager.translate(source_text, source_lang, target_lang)
            print(f"Translated ({manager.config['language_names'][target_lang]}):")
            print(f"  {translated}")
        except Exception as e:
            print(f"Translation failed: {e}")
    
    print("\n" + "="*60)
    
    # Interactive translation example
    print("\nInteractive Translation Demo")
    print("-" * 40)
    print("Enter 'quit' to exit\n")
    
    while True:
        print("\nAvailable languages: zh (Chinese), en (English), el (Greek)")
        source = input("Source language code: ").strip().lower()
        if source == 'quit':
            break
        if source not in ['zh', 'en', 'el']:
            print("Invalid language code. Please use: zh, en, or el")
            continue
        
        target = input("Target language code: ").strip().lower()
        if target == 'quit':
            break
        if target not in ['zh', 'en', 'el']:
            print("Invalid language code. Please use: zh, en, or el")
            continue
        
        if source == target:
            print("Source and target languages are the same!")
            continue
        
        text = input(f"Enter text in {manager.config['language_names'][source]}: ").strip()
        if text == 'quit':
            break
        
        if not text:
            print("Please enter some text to translate")
            continue
        
        try:
            print(f"\nTranslating from {manager.config['language_names'][source]} to {manager.config['language_names'][target]}...")
            translated = manager.translate(text, source, target)
            print(f"Result: {translated}")
        except Exception as e:
            print(f"Translation failed: {e}")
    
    print("\nGoodbye!")
    
    # Clear cache to free memory
    manager.clear_cache()


if __name__ == "__main__":
    main()
