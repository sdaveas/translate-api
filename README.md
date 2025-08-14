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
# Start the server
pipenv run python api.py
```

The API will be available at `http://localhost:8080`

**Note:** For production deployment, consider using a WSGI server like Gunicorn:
```bash
pipenv run gunicorn -w 4 -b 0.0.0.0:8080 api:app
```

## 📁 Project Structure

```
translate-api/
├── api.py                    # Flask REST API server
├── translation_manager.py    # Core translation logic
├── translation_config.json   # Routes and model configuration
├── API_DOCUMENTATION.md     # Detailed API documentation
├── translate.py             # CLI tool for quick translations
├── translate_example.py     # Interactive demo
├── test_translation.py      # Test suite
└── client_example.py        # Example API client
```

## 📡 API Reference

### Quick Example

```bash
# Translate text from English to Chinese
curl -X POST http://localhost:8080/translate \
  -H "Content-Type: application/json" \
  -d '{"from": "en", "to": "zh", "text": "Hello, world"}'

# Response
{
  "original_text": "Hello, world",
  "translated_text": "你好，世界",
  "from": "en",
  "to": "zh"
}
```

### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| GET | `/languages` | Available languages and routes |
| POST | `/translate` | Translate text |
| DELETE | `/cache` | Clear model cache |

📚 **For detailed API documentation with request/response examples, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md)**

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

# Multiple translations (call translate multiple times)
for text in ["Hello", "World", "Friend"]:
    response = requests.post(
        f"{API_URL}/translate",
        json={"from": "en", "to": "el", "text": text}
    )
    result = response.json()
    print(f"{text} → {result['translated_text']}")
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
