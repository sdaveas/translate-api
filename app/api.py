#!/usr/bin/env python3
"""
Flask API service for Google Translate
Provides REST endpoints for text translation and language information
"""

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import json
from app.translator import SimpleTranslator, LANGUAGES
from app.logger import setup_logger

# Configure logging
logger = setup_logger('translation_api')

# Create Flask app
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # Ensure proper UTF-8 encoding for non-ASCII characters
CORS(app)  # Enable CORS for all routes

# Initialize translator (singleton)
translator = None

def get_translator():
    """Get or create the translator singleton."""
    global translator
    if translator is None:
        logger.info("Initializing Google Translator...")
        translator = SimpleTranslator()
    return translator


@app.route('/')
def index():
    """API root endpoint with service information."""
    return jsonify({
        "service": "Google Translate API",
        "version": "2.0.0",
        "description": "REST API for text translation using Google Translate",
        "endpoints": {
            "/": "Service information",
            "/health": "Health check",
            "/translate": "Translate text (POST)",
            "/languages": "Get available languages (GET)"
        }
    })


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "translation-api"
    })


@app.route('/languages', methods=['GET'])
def get_languages():
    """
    Get list of available languages for translation.

    Returns:
        JSON object with language codes and names
    """
    try:
        t = get_translator()
        languages = t.get_supported_languages()

        # Format the response
        formatted_languages = [
            {"code": code, "name": name}
            for code, name in sorted(languages.items())
        ]

        return jsonify({
            "languages": formatted_languages,
            "total": len(formatted_languages)
        })

    except Exception as e:
        logger.error(f"Error fetching languages: {str(e)}")
        return jsonify({
            "error": "Failed to fetch available languages",
            "details": str(e)
        }), 500


@app.route('/translate', methods=['POST'])
def translate():
    """
    Translate text from one language to another.

    Expected JSON payload:
    {
        "text": "Text to translate",
        "dest": "es",  # Destination language code (required)
        "src": "auto",  # Source language code (optional, default: "auto")
        "pronunciation": false  # Include pronunciation (optional, default: false)
    }

    Returns:
        JSON object with translated text and optional pronunciation
    """
    try:
        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Extract and validate parameters
        text = data.get('text')
        dest = data.get('dest')
        src = data.get('src', 'auto')
        include_pronunciation = data.get('pronunciation', False)

        # Validate required fields
        if not text:
            return jsonify({"error": "Missing 'text' field"}), 400
        if not dest:
            return jsonify({"error": "Missing 'dest' field"}), 400

        # Validate language codes
        if dest not in LANGUAGES and dest != 'auto':
            return jsonify({
                "error": f"Invalid destination language code: {dest}",
                "hint": "Use /languages endpoint to see available language codes"
            }), 400

        if src != 'auto' and src not in LANGUAGES:
            return jsonify({
                "error": f"Invalid source language code: {src}",
                "hint": "Use /languages endpoint to see available language codes, or use 'auto' for automatic detection"
            }), 400

        # Perform translation
        t = get_translator()
        result = t.translate(text, dest=dest, src=src)

        if not result:
            return jsonify({
                "error": "Translation failed",
                "details": "Unable to translate the provided text"
            }), 500

        # Build response
        response = {
            "original_text": text,
            "translated_text": result.text,
            "source_language": result.src,
            "destination_language": dest
        }

        # Add pronunciation if requested and available
        if include_pronunciation and result.pronunciation:
            response["pronunciation"] = result.pronunciation

        # Add detected language info if auto-detect was used
        if src == 'auto':
            response["detected_language"] = {
                "code": result.src,
                "name": LANGUAGES.get(result.src, "Unknown")
            }

        # Return response with proper UTF-8 encoding
        return make_response(
            json.dumps(response, ensure_ascii=False, indent=2),
            200,
            {'Content-Type': 'application/json; charset=utf-8'}
        )

    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        return jsonify({
            "error": "Translation failed",
            "details": str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "error": "Endpoint not found",
        "message": "The requested endpoint does not exist",
        "available_endpoints": {
            "/": "Service information",
            "/health": "Health check",
            "/translate": "Translate text (POST)",
            "/languages": "Get available languages (GET)"
        }
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({
        "error": "Method not allowed",
        "message": f"The {request.method} method is not allowed for this endpoint"
    }), 405


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500


if __name__ == '__main__':
    import sys
    import os

    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))

    # Check if running in production or development
    is_production = os.environ.get('FLASK_ENV') == 'production'

    if is_production:
        # Production settings
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        # Development settings
        app.run(host='0.0.0.0', port=port, debug=True, use_reloader=True)
