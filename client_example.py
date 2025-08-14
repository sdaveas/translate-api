#!/usr/bin/env python3
"""
Example client for the Translation API.
Shows how to use the API from Python code.
"""

import requests
import json
from typing import Optional, List

class TranslationClient:
    """Simple client for the Translation API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the client.
        
        Args:
            base_url: Base URL of the API service
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def health_check(self) -> dict:
        """Check if the service is healthy."""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def get_languages(self) -> dict:
        """Get available languages and routes."""
        response = self.session.get(f"{self.base_url}/languages")
        response.raise_for_status()
        return response.json()
    
    def translate(self, text: str, from_lang: str, to_lang: str) -> dict:
        """
        Translate text from one language to another.
        
        Args:
            text: Text to translate
            from_lang: Source language code (zh, en, el)
            to_lang: Target language code (zh, en, el)
            
        Returns:
            Translation response with original and translated text
        """
        data = {
            "from": from_lang,
            "to": to_lang,
            "text": text
        }
        response = self.session.post(
            f"{self.base_url}/translate",
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def translate_batch(self, texts: List[str], from_lang: str, to_lang: str) -> dict:
        """
        Translate multiple texts at once.
        
        Args:
            texts: List of texts to translate
            from_lang: Source language code
            to_lang: Target language code
            
        Returns:
            Batch translation response
        """
        data = {
            "from": from_lang,
            "to": to_lang,
            "texts": texts
        }
        response = self.session.post(
            f"{self.base_url}/translate/batch",
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def clear_cache(self) -> dict:
        """Clear the model cache on the server."""
        response = self.session.delete(f"{self.base_url}/cache")
        response.raise_for_status()
        return response.json()


def main():
    """Example usage of the Translation API client."""
    
    # Create client
    client = TranslationClient()
    
    print("=" * 60)
    print("Translation API Client Example")
    print("=" * 60)
    
    # Check health
    print("\n1. Health Check:")
    health = client.health_check()
    print(f"   Status: {health['status']}")
    print(f"   Message: {health['message']}")
    
    # Get available languages
    print("\n2. Available Languages:")
    info = client.get_languages()
    print("   Languages:")
    for code, name in info['languages'].items():
        print(f"     {code}: {name}")
    print("   Routes:")
    for source, targets in info['routes'].items():
        print(f"     From {source} to: {', '.join(targets)}")
    
    # Single translation examples
    print("\n3. Single Translations:")
    
    # Chinese to English
    result = client.translate("你好，世界！", "zh", "en")
    print(f"\n   Chinese → English:")
    print(f"     Original: {result['original_text']}")
    print(f"     Translated: {result['translated_text']}")
    
    # English to Greek
    result = client.translate("Hello world!", "en", "el")
    print(f"\n   English → Greek:")
    print(f"     Original: {result['original_text']}")
    print(f"     Translated: {result['translated_text']}")
    
    # Chain translation: Chinese to Greek
    result = client.translate("你好朋友", "zh", "el")
    print(f"\n   Chinese → Greek (chain):")
    print(f"     Original: {result['original_text']}")
    print(f"     Translated: {result['translated_text']}")
    if result.get('translation_path'):
        print(f"     Path: {' → '.join(result['translation_path'])}")
    
    # Batch translation
    print("\n4. Batch Translation:")
    texts = ["Hello", "World", "How are you?"]
    batch_result = client.translate_batch(texts, "en", "zh")
    print(f"\n   English → Chinese (batch):")
    for trans in batch_result['translations']:
        print(f"     '{trans['original_text']}' → '{trans['translated_text']}'")
    
    # Interactive mode
    print("\n" + "=" * 60)
    print("Interactive Mode (type 'quit' to exit)")
    print("=" * 60)
    
    while True:
        print("\nAvailable languages: zh (Chinese), en (English), el (Greek)")
        
        from_lang = input("From language (zh/en/el): ").strip().lower()
        if from_lang == 'quit':
            break
        if from_lang not in ['zh', 'en', 'el']:
            print("Invalid language code!")
            continue
        
        to_lang = input("To language (zh/en/el): ").strip().lower()
        if to_lang == 'quit':
            break
        if to_lang not in ['zh', 'en', 'el']:
            print("Invalid language code!")
            continue
        
        if from_lang == to_lang:
            print("Source and target languages are the same!")
            continue
        
        text = input("Text to translate: ").strip()
        if text == 'quit':
            break
        if not text:
            print("Please enter some text!")
            continue
        
        try:
            result = client.translate(text, from_lang, to_lang)
            print(f"\nTranslation: {result['translated_text']}")
            if result.get('translation_path'):
                print(f"(via: {' → '.join(result['translation_path'])})")
        except Exception as e:
            print(f"Error: {e}")
    
    print("\nGoodbye!")


if __name__ == "__main__":
    main()
