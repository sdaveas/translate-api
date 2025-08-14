# Translation API

A REST API service for translating text between Chinese, English, and Greek using Hugging Face's Helsinki-NLP OPUS models.

## 🌟 Overview

This translation API provides high-quality translations between:
- 🇨🇳 **Chinese** (zh)
- 🇬🇧 **English** (en) 
- 🇬🇷 **Greek** (el)

The system automatically handles direct translations where models are available, and performs chain translations through English when needed.

## ✨ Features

- 🔄 **Smart Routing**: Automatically finds the best translation path
- 🔗 **Chain Translation**: Seamlessly translates through intermediate languages when needed
- ⚡ **Model Caching**: Loaded models are cached for faster subsequent translations
- 🛠️ **Multiple Interfaces**: REST API, command-line tools, and Python library
- 🚫 **Anti-Repetition**: Advanced generation parameters prevent repetitive output
- 📦 **Batch Processing**: Translate multiple texts in a single request

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/translate-api.git
cd translate-api

# Install dependencies with pipenv (recommended)
pipenv install

# Or using pip
pip install transformers torch torchvision torchaudio sentencepiece sacremoses flask flask-cors
```

### Start the API Server

```bash
# Start in foreground
pipenv run python api.py

# Or start in background
./start_server.sh

# Stop background server
./stop_server.sh
```

The API will be available at `http://localhost:8080`

## 📁 Project Structure

```
translate-api/
├── api.py                    # Flask REST API server
├── translation_manager.py    # Core translation logic
├── translation_config.json   # Routes and model configuration
├── translate.py             # CLI tool for quick translations
├── translate_example.py     # Interactive demo
├── test_translation.py      # Test suite
├── client_example.py        # Example API client
├── start_server.sh          # Start API server script
└── stop_server.sh           # Stop API server script
```

## 📡 API Reference

### Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| GET | `/languages` | Available languages and routes |
| POST | `/translate` | Translate single text |
| POST | `/translate/batch` | Translate multiple texts |
| DELETE | `/cache` | Clear model cache |

### 🔍 Detailed Request & Response Examples

#### 1. Get API Information

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
    "/translate/batch": "Translate multiple texts (POST)",
    "/cache": "Clear model cache (DELETE)"
  }
}
```

#### 2. Health Check

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

#### 3. Get Available Languages

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

#### 4. Translate Text (Single)

**Direct Translation (English to Chinese):**
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

**Chain Translation (Chinese to Greek via English):**
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

#### 5. Batch Translation

**Request:**
```bash
curl -X POST http://localhost:8080/translate/batch \
  -H "Content-Type: application/json" \
  -d '{
    "from": "en",
    "to": "zh",
    "texts": [
      "Good morning",
      "How are you?",
      "Thank you very much"
    ]
  }'
```

**Response:**
```json
{
  "translations": [
    {
      "original_text": "Good morning",
      "translated_text": "早上好"
    },
    {
      "original_text": "How are you?",
      "translated_text": "你好吗?"
    },
    {
      "original_text": "Thank you very much",
      "translated_text": "非常感谢你"
    }
  ],
  "from": "en",
  "to": "zh"
}
```

#### 6. Clear Model Cache

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

### Error Responses

**Missing Required Field:**
```json
{
  "error": "Missing 'text' to translate"
}
```

**Invalid Language Code:**
```json
{
  "error": "Invalid source language: fr",
  "valid_languages": ["zh", "en", "el"]
}
```

**Same Source and Target Language:**
```json
{
  "error": "Source and target languages are the same"
}
```

## 💻 Usage Examples

### Command Line Interface

```bash
# Simple translations
pipenv run python translate.py en zh "Hello world"
pipenv run python translate.py zh en "你好世界"
pipenv run python translate.py en el "Good morning"

# Chain translation (automatically routed through English)
pipenv run python translate.py zh el "你好朋友"
pipenv run python translate.py el zh "Καλημέρα"
```

### Python Library

```python
from translation_manager import TranslationManager

# Initialize the manager
manager = TranslationManager()

# Single translation
result = manager.translate("Hello world", "en", "zh")
print(result)  # Output: 你好，世界

# Chain translation (automatic routing)
result = manager.translate("你好朋友", "zh", "el")
print(result)  # Output: Γεια σου, φίλε μου.

# Batch translation
texts = ["Good morning", "Thank you", "Goodbye"]
results = manager.translate_batch(texts, "en", "zh")
for original, translated in zip(texts, results):
    print(f"{original} → {translated}")

# Free memory when done
manager.clear_cache()
```

### Using the REST API Client

```python
import requests

API_URL = "http://localhost:8080"

# Single translation
response = requests.post(
    f"{API_URL}/translate",
    json={
        "from": "en",
        "to": "zh",
        "text": "Hello, how are you?"
    }
)
result = response.json()
print(f"Translated: {result['translated_text']}")

# Batch translation
response = requests.post(
    f"{API_URL}/translate/batch",
    json={
        "from": "en",
        "to": "el",
        "texts": ["Hello", "World", "Friend"]
    }
)
results = response.json()
for item in results['translations']:
    print(f"{item['original_text']} → {item['translated_text']}")
```

## 🗺️ Translation Routes

### Direct Translation Paths
| From | To | Model |
|------|----|-------|
| Chinese | English | `Helsinki-NLP/opus-mt-zh-en` |
| English | Chinese | `Helsinki-NLP/opus-mt-en-zh` |
| English | Greek | `Helsinki-NLP/opus-mt-en-el` |
| Greek | English | `Helsinki-NLP/opus-mt-tc-big-el-en` |

### Chain Translation Paths (via English)
| From | To | Path |
|------|----|------|
| Chinese | Greek | Chinese → English → Greek |
| Greek | Chinese | Greek → English → Chinese |

## Configuration Structure
The `translation_config.json` file defines:
- `translation_routes`: Maps source to target languages with model paths
- `language_names`: Human-readable language names
- `default_intermediate`: Language used for chain translations (default: "en")
- `cache_models`: Whether to cache loaded models (default: true)
- `device`: Device for computation ("auto", "cpu", "cuda", or "mps")

## Adding New Languages
To add a new language:
1. Find available models on [Hugging Face](https://huggingface.co/Helsinki-NLP)
2. Add the language code to `language_names` in config
3. Define translation routes in `translation_routes`
4. Test the new routes

## Performance Notes
- First translation loads models (slower)
- Subsequent translations use cached models (faster)
- Chain translations take longer than direct ones
- MPS (Apple Silicon) provides good performance on Mac
- Use `manager.clear_cache()` to free memory when done

## 🌍 Language Support

### Supported Languages
- **Chinese (zh)**: Simplified Chinese
- **English (en)**: English
- **Greek (el)**: Modern Greek

### Example Translations

| Source | Target | Input | Output |
|--------|--------|-------|--------|
| English | Chinese | Hello, world | 你好，世界 |
| Chinese | English | 你好朋友 | Hello, friend |
| English | Greek | Good morning | Καλημέρα |
| Greek | English | Γεια σου | Hello |
| Chinese | Greek | 你好 | Γεια σου (via English) |
| Greek | Chinese | Καλημέρα | 早上好 (via English) |

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Slow first translation** | Models are being loaded for the first time. Subsequent translations will be faster due to caching. |
| **Out of memory error** | Call the `/cache` endpoint with DELETE method or use `manager.clear_cache()` in Python. |
| **Repetitive translations** | Update to the latest version which includes anti-repetition parameters. |
| **Connection refused** | Ensure the server is running on port 8080. Check with `curl http://localhost:8080/health`. |
| **Model not found** | Verify model names in `translation_config.json` match Hugging Face repository names. |

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue on GitHub.
