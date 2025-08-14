"""
Flask service for the Translation API.
Simple REST API for translating text between Chinese, English, and Greek.
"""

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import logging
import os
import json
from translation_manager import TranslationManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # Ensure proper UTF-8 encoding for non-ASCII characters
CORS(app)  # Enable CORS for all routes

# Initialize translation manager (singleton)
translation_manager = None

def get_translation_manager():
    """Get or create the translation manager singleton."""
    global translation_manager
    if translation_manager is None:
        logger.info("Initializing Translation Manager...")
        translation_manager = TranslationManager()
    return translation_manager


@app.route('/')
def index():
    """API root endpoint."""
    return jsonify({
        "service": "Translation API",
        "version": "1.0.0",
        "endpoints": {
            "/": "API information",
            "/health": "Health check",
            "/languages": "Get available languages and routes",
            "/translate": "Translate text (POST)",
            "/translate/batch": "Translate multiple texts (POST)",
            "/cache": "Clear model cache (DELETE)"
        }
    })


@app.route('/api')
def api_info():
    """API information endpoint (same as root)."""
    return index()


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "message": "Service is healthy"})


@app.route('/languages')
def languages():
    """Get available languages and translation routes."""
    manager = get_translation_manager()
    return jsonify({
        "languages": manager.config.get("language_names", {}),
        "routes": manager.get_available_routes()
    })


@app.route('/translate', methods=['POST'])
def translate():
    """
    Translate text from one language to another.
    
    Expected JSON payload:
    {
        "from": "zh",  # Source language code
        "to": "en",    # Target language code  
        "text": "你好"  # Text to translate
    }
    """
    # Get JSON data
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    # Validate required fields
    from_lang = data.get('from')
    to_lang = data.get('to')
    text = data.get('text')
    
    if not from_lang:
        return jsonify({"error": "Missing 'from' language"}), 400
    if not to_lang:
        return jsonify({"error": "Missing 'to' language"}), 400
    if not text:
        return jsonify({"error": "Missing 'text' to translate"}), 400
    
    # Validate language codes
    valid_langs = ["zh", "en", "el"]
    if from_lang not in valid_langs:
        return jsonify({
            "error": f"Invalid source language: {from_lang}",
            "valid_languages": valid_langs
        }), 400
    if to_lang not in valid_langs:
        return jsonify({
            "error": f"Invalid target language: {to_lang}",
            "valid_languages": valid_langs
        }), 400
    if from_lang == to_lang:
        return jsonify({"error": "Source and target languages are the same"}), 400
    
    try:
        manager = get_translation_manager()
        
        # Check if route exists
        route = manager.get_translation_route(from_lang, to_lang)
        if not route:
            return jsonify({
                "error": f"No translation route available from {from_lang} to {to_lang}"
            }), 400
        
        # Perform translation
        translated_text = manager.translate(text, from_lang, to_lang)
        
        # Build response
        response = {
            "original_text": text,
            "translated_text": translated_text,
            "from": from_lang,
            "to": to_lang
        }
        
        # Add translation path for chain translations
        if len(route["path"]) > 1:
            path_names = []
            for step in route["path"]:
                parts = step.split("-")
                path_names.append(manager.config["language_names"].get(parts[0], parts[0]))
            path_names.append(manager.config["language_names"].get(to_lang, to_lang))
            response["translation_path"] = path_names
        
        # Create response with proper UTF-8 encoding
        resp = make_response(json.dumps(response, ensure_ascii=False, indent=2))
        resp.headers['Content-Type'] = 'application/json; charset=utf-8'
        return resp
        
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        return jsonify({"error": f"Translation failed: {str(e)}"}), 500


@app.route('/translate/batch', methods=['POST'])
def translate_batch():
    """
    Translate multiple texts at once.
    
    Expected JSON payload:
    {
        "from": "en",
        "to": "zh",
        "texts": ["Hello", "World", "Friend"]
    }
    """
    # Get JSON data
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    # Validate required fields
    from_lang = data.get('from')
    to_lang = data.get('to')
    texts = data.get('texts')
    
    if not from_lang:
        return jsonify({"error": "Missing 'from' language"}), 400
    if not to_lang:
        return jsonify({"error": "Missing 'to' language"}), 400
    if not texts:
        return jsonify({"error": "Missing 'texts' to translate"}), 400
    if not isinstance(texts, list):
        return jsonify({"error": "'texts' must be a list"}), 400
    
    # Validate language codes
    valid_langs = ["zh", "en", "el"]
    if from_lang not in valid_langs:
        return jsonify({
            "error": f"Invalid source language: {from_lang}",
            "valid_languages": valid_langs
        }), 400
    if to_lang not in valid_langs:
        return jsonify({
            "error": f"Invalid target language: {to_lang}",
            "valid_languages": valid_langs
        }), 400
    if from_lang == to_lang:
        return jsonify({"error": "Source and target languages are the same"}), 400
    
    try:
        manager = get_translation_manager()
        
        # Check if route exists
        route = manager.get_translation_route(from_lang, to_lang)
        if not route:
            return jsonify({
                "error": f"No translation route available from {from_lang} to {to_lang}"
            }), 400
        
        # Build translation path if it's a chain translation
        translation_path = None
        if len(route["path"]) > 1:
            path_names = []
            for step in route["path"]:
                parts = step.split("-")
                path_names.append(manager.config["language_names"].get(parts[0], parts[0]))
            path_names.append(manager.config["language_names"].get(to_lang, to_lang))
            translation_path = path_names
        
        # Translate all texts
        translations = []
        for text in texts:
            translated = manager.translate(text, from_lang, to_lang)
            translation_item = {
                "original_text": text,
                "translated_text": translated
            }
            translations.append(translation_item)
        
        # Build response
        response = {
            "translations": translations,
            "from": from_lang,
            "to": to_lang
        }
        
        if translation_path:
            response["translation_path"] = translation_path
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Batch translation error: {str(e)}")
        return jsonify({"error": f"Batch translation failed: {str(e)}"}), 500


@app.route('/cache', methods=['DELETE'])
def clear_cache():
    """Clear the model cache to free memory."""
    try:
        manager = get_translation_manager()
        manager.clear_cache()
        return jsonify({"status": "ok", "message": "Model cache cleared successfully"})
    except Exception as e:
        logger.error(f"Cache clear error: {str(e)}")
        return jsonify({"error": f"Failed to clear cache: {str(e)}"}), 500


if __name__ == '__main__':
    import sys
    # Run the Flask development server
    # Check if running in background (no tty) to avoid termios issues
    is_background = not sys.stdin.isatty()
    
    if is_background:
        # Running in background - disable debug mode to avoid interrupted system call
        app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
    else:
        # Running in foreground - enable debug mode
        app.run(host='0.0.0.0', port=8080, debug=True)
