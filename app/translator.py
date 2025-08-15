#!/usr/bin/env python3
"""
Simple translation utility using Google Translate
"""

from googletrans import Translator, LANGUAGES
import asyncio


class SimpleTranslator:
    def __init__(self):
        self.translator = Translator()
        # Create event loop for async operations
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

    def _run_async(self, coro):
        """Helper to run async coroutines in sync context"""
        try:
            # If we're already in an async context, create a new loop
            if asyncio.get_event_loop().is_running():
                loop = asyncio.new_event_loop()
                return loop.run_until_complete(coro)
            else:
                return self.loop.run_until_complete(coro)
        except RuntimeError:
            # Create a new loop if needed
            loop = asyncio.new_event_loop()
            return loop.run_until_complete(coro)

    def translate(self, text, dest='en', src='auto'):
        """
        Translate text to the specified language

        Args:
            text: Text to translate
            dest: Destination language code (default: 'en')
            src: Source language code (default: 'auto' for auto-detection)

        Returns:
            Translation result object
        """
        try:
            # googletrans 4.x uses async methods
            result = self._run_async(self.translator.translate(text, dest=dest, src=src))
            return result
        except Exception as e:
            print(f"Translation error: {e}")
            return None

    def detect_language(self, text):
        """
        Detect the language of the given text

        Args:
            text: Text to detect language for

        Returns:
            Detected language object
        """
        try:
            # googletrans 4.x uses async methods
            detection = self._run_async(self.translator.detect(text))
            return detection
        except Exception as e:
            print(f"Language detection error: {e}")
            return None

    def bulk_translate(self, texts, dest='en', src='auto'):
        """
        Translate multiple texts at once

        Args:
            texts: List of texts to translate
            dest: Destination language code
            src: Source language code

        Returns:
            List of translation results
        """
        results = []
        for text in texts:
            result = self.translate(text, dest=dest, src=src)
            if result:
                results.append({
                    'original': text,
                    'translated': result.text,
                    'pronunciation': result.pronunciation,
                    'source_lang': result.src
                })
        return results

    def get_supported_languages(self):
        """
        Get list of supported languages

        Returns:
            Dictionary of language codes and names
        """
        return LANGUAGES
