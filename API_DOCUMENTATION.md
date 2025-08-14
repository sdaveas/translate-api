# API Documentation

## Base URL
```
http://localhost:8080
```

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| GET | `/languages` | Available languages and routes |
| POST | `/translate` | Translate text |
| DELETE | `/cache` | Clear model cache |

## Detailed Request & Response Examples

### 1. Get API Information

Returns information about the API service and available endpoints.

**Request:**
```bash
curl http://localhost:8080/
```

**Response:**
```json
{
  "service": "Translation API",
  "version": "1.0.0",
  "endpoints": {
    "/": "API information",
    "/health": "Health check",
    "/languages": "Get available languages and routes",
    "/translate": "Translate text (POST)",
    "/cache": "Clear model cache (DELETE)"
  }
}
```

### 2. Health Check

Check if the service is running and healthy.

**Request:**
```bash
curl http://localhost:8080/health
```

**Response:**
```json
{
  "status": "ok",
  "message": "Service is healthy"
}
```

### 3. Get Available Languages

Returns supported languages and available translation routes.

**Request:**
```bash
curl http://localhost:8080/languages
```

**Response:**
```json
{
  "languages": {
    "zh": "Chinese",
    "en": "English",
    "el": "Greek"
  },
  "routes": {
    "Chinese": ["English", "Greek"],
    "English": ["Chinese", "Greek"],
    "Greek": ["English", "Chinese"]
  }
}
```

### 4. Translate Text (Single)

Translate a single text from one language to another.

#### Direct Translation Example (English to Chinese)

**Request:**
```bash
curl -X POST http://localhost:8080/translate \
  -H "Content-Type: application/json" \
  -d '{
    "from": "en",
    "to": "zh",
    "text": "Hello, how are you today?"
  }'
```

**Response:**
```json
{
  "original_text": "Hello, how are you today?",
  "translated_text": "哈罗,你今天好吗?",
  "from": "en",
  "to": "zh"
}
```

#### Chain Translation Example (Chinese to Greek via English)

**Request:**
```bash
curl -X POST http://localhost:8080/translate \
  -H "Content-Type: application/json" \
  -d '{
    "from": "zh",
    "to": "el",
    "text": "你好，朋友"
  }'
```

**Response:**
```json
{
  "original_text": "你好，朋友",
  "translated_text": "Γεια σου, φίλε μου.",
  "from": "zh",
  "to": "el",
  "translation_path": ["Chinese", "English", "Greek"]
}
```

**Note:** The `translation_path` field only appears when chain translation is used (i.e., when translating through an intermediate language).

#### More Translation Examples

**Chinese to English:**
```bash
curl -X POST http://localhost:8080/translate \
  -H "Content-Type: application/json" \
  -d '{
    "from": "zh",
    "to": "en",
    "text": "你好，世界"
  }'
```

**Response:**
```json
{
  "original_text": "你好，世界",
  "translated_text": "Hello, world.",
  "from": "zh",
  "to": "en"
}
```

**English to Greek:**
```bash
curl -X POST http://localhost:8080/translate \
  -H "Content-Type: application/json" \
  -d '{
    "from": "en",
    "to": "el",
    "text": "Good morning, how are you?"
  }'
```

**Response:**
```json
{
  "original_text": "Good morning, how are you?",
  "translated_text": "Καλημέρα, πώς είσαι;",
  "from": "en",
  "to": "el"
}
```

**Greek to English:**
```bash
curl -X POST http://localhost:8080/translate \
  -H "Content-Type: application/json" \
  -d '{
    "from": "el",
    "to": "en",
    "text": "Γεια σου κόσμε"
  }'
```

**Response:**
```json
{
  "original_text": "Γεια σου κόσμε",
  "translated_text": "Hello world",
  "from": "el",
  "to": "en"
}
```

### 5. Clear Model Cache

Clear all cached models to free memory.

**Request:**
```bash
curl -X DELETE http://localhost:8080/cache
```

**Response:**
```json
{
  "status": "ok",
  "message": "Model cache cleared successfully"
}
```

## Error Responses

The API returns appropriate HTTP status codes and error messages for various error conditions.

### 400 Bad Request - Missing Required Field

**Request:**
```bash
curl -X POST http://localhost:8080/translate \
  -H "Content-Type: application/json" \
  -d '{
    "from": "en",
    "to": "zh"
  }'
```

**Response:**
```json
{
  "error": "Missing 'text' to translate"
}
```

### 400 Bad Request - Invalid Language Code

**Request:**
```bash
curl -X POST http://localhost:8080/translate \
  -H "Content-Type: application/json" \
  -d '{
    "from": "fr",
    "to": "zh",
    "text": "Bonjour"
  }'
```

**Response:**
```json
{
  "error": "Invalid source language: fr",
  "valid_languages": ["zh", "en", "el"]
}
```

### 400 Bad Request - Same Source and Target Language

**Request:**
```bash
curl -X POST http://localhost:8080/translate \
  -H "Content-Type: application/json" \
  -d '{
    "from": "en",
    "to": "en",
    "text": "Hello"
  }'
```

**Response:**
```json
{
  "error": "Source and target languages are the same"
}
```

### 400 Bad Request - No JSON Data

**Request:**
```bash
curl -X POST http://localhost:8080/translate
```

**Response:**
```json
{
  "error": "No JSON data provided"
}
```

### 500 Internal Server Error

If translation fails due to model issues or other internal errors:

**Response:**
```json
{
  "error": "Translation failed: [error details]"
}
```

## Request Parameters

### /translate Endpoint

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `from` | string | Yes | Source language code (`zh`, `en`, or `el`) |
| `to` | string | Yes | Target language code (`zh`, `en`, or `el`) |
| `text` | string | Yes | Text to translate |


## Language Codes

| Code | Language |
|------|----------|
| `zh` | Chinese (Simplified) |
| `en` | English |
| `el` | Greek |

## Translation Routes

### Direct Translation Paths
| From | To | Model Used |
|------|----|------------|
| Chinese (`zh`) | English (`en`) | Helsinki-NLP/opus-mt-zh-en |
| English (`en`) | Chinese (`zh`) | Helsinki-NLP/opus-mt-en-zh |
| English (`en`) | Greek (`el`) | Helsinki-NLP/opus-mt-en-el |
| Greek (`el`) | English (`en`) | Helsinki-NLP/opus-mt-tc-big-el-en |

### Chain Translation Paths
| From | To | Path |
|------|----|------|
| Chinese (`zh`) | Greek (`el`) | Chinese → English → Greek |
| Greek (`el`) | Chinese (`zh`) | Greek → English → Chinese |

## Rate Limits

Currently, there are no rate limits imposed by the API. However, please note:
- First translation request may take 10-15 seconds as models are loaded
- Subsequent requests are faster due to model caching
- Chain translations take approximately twice as long as direct translations

## Python Client Example

```python
import requests
import json

class TranslationClient:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
    
    def translate(self, text, from_lang, to_lang):
        """Translate a single text."""
        response = requests.post(
            f"{self.base_url}/translate",
            json={
                "from": from_lang,
                "to": to_lang,
                "text": text
            }
        )
        return response.json()
    
    def get_languages(self):
        """Get available languages and routes."""
        response = requests.get(f"{self.base_url}/languages")
        return response.json()
    
    def health_check(self):
        """Check if service is healthy."""
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def clear_cache(self):
        """Clear model cache."""
        response = requests.delete(f"{self.base_url}/cache")
        return response.json()

# Usage example
client = TranslationClient()

# Single translation
result = client.translate("Hello world", "en", "zh")
print(f"Translation: {result['translated_text']}")

# Multiple translations
for text in ["Good morning", "Thank you", "Goodbye"]:
    result = client.translate(text, "en", "el")
    print(f"{text} → {result['translated_text']}")
```

## cURL Examples for Common Use Cases

### Translate a greeting from English to all supported languages

```bash
# English to Chinese
curl -X POST http://localhost:8080/translate \
  -H "Content-Type: application/json" \
  -d '{"from": "en", "to": "zh", "text": "Hello, nice to meet you!"}'

# English to Greek  
curl -X POST http://localhost:8080/translate \
  -H "Content-Type: application/json" \
  -d '{"from": "en", "to": "el", "text": "Hello, nice to meet you!"}'
```

### Translate a business email opening

```bash
curl -X POST http://localhost:8080/translate \
  -H "Content-Type: application/json" \
  -d '{
    "from": "en",
    "to": "zh",
    "text": "Dear Sir or Madam, I hope this email finds you well."
  }'
```

### Translate common phrases for travel

```bash
# Using a loop to translate multiple phrases
for phrase in "Where is the bathroom?" "How much does this cost?" "Can you help me?"; do
  curl -X POST http://localhost:8080/translate \
    -H "Content-Type: application/json" \
    -d "{\"from\": \"en\", \"to\": \"el\", \"text\": \"$phrase\"}"
  echo
done
```
