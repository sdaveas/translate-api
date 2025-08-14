#!/usr/bin/env python3
"""
Simple translation utility using the Translation Manager.
Usage: python translate_simple.py [source_lang] [target_lang] "text to translate"
"""

import sys
from translation_manager import TranslationManager
import logging

# Reduce logging noise for simple usage
logging.basicConfig(level=logging.WARNING)

def main():
    if len(sys.argv) < 4:
        print("Usage: python translate_simple.py [source_lang] [target_lang] \"text to translate\"")
        print("\nAvailable languages:")
        print("  zh - Chinese")
        print("  en - English")
        print("  el - Greek")
        print("\nExamples:")
        print('  python translate_simple.py zh en "你好世界"')
        print('  python translate_simple.py en el "Hello world"')
        print('  python translate_simple.py zh el "你好世界"  # Chain translation via English')
        sys.exit(1)
    
    source_lang = sys.argv[1].lower()
    target_lang = sys.argv[2].lower()
    text = sys.argv[3]
    
    # Validate languages
    valid_langs = ['zh', 'en', 'el']
    if source_lang not in valid_langs or target_lang not in valid_langs:
        print(f"Error: Invalid language code. Use one of: {', '.join(valid_langs)}")
        sys.exit(1)
    
    if source_lang == target_lang:
        print("Error: Source and target languages are the same!")
        sys.exit(1)
    
    # Initialize manager and translate
    try:
        manager = TranslationManager()
        result = manager.translate(text, source_lang, target_lang)
        print(result)
    except Exception as e:
        print(f"Translation failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
