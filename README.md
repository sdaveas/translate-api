# Translate API

A configurable translation system supporting Chinese, English, and Greek translations using Hugging Face's Helsinki-NLP OPUS models.

## Overview
This translation system supports translations between Chinese (zh), English (en), and Greek (el) using Hugging Face's Helsinki-NLP OPUS models. It automatically handles chain translations when direct models aren't available.

## Features
- **Configurable routing**: Define translation paths in `translation_config.json`
- **Automatic chain translation**: Translates through intermediate languages when needed
- **Model caching**: Loaded models are cached for better performance
- **Multiple interfaces**: Use the manager class directly or through utility scripts

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/translate-api.git
cd translate-api

# Install dependencies
pipenv install

# Or using pip
pip install transformers torch torchvision torchaudio sentencepiece sacremoses
```

## Files
- `translation_config.json` - Configuration file defining translation routes
- `translation_manager.py` - Main TranslationManager class
- `translate_simple.py` - Command-line utility for quick translations
- `translate_example.py` - Interactive demo with examples
- `test_translation.py` - Test script for verification

## Usage

### Simple Command Line
```bash
# Direct translations
pipenv run python translate_simple.py zh en "你好世界"
pipenv run python translate_simple.py en el "Hello world"

# Chain translation (Chinese to Greek via English)
pipenv run python translate_simple.py zh el "你好朋友"
```

### Python API
```python
from translation_manager import TranslationManager

# Initialize manager
manager = TranslationManager("translation_config.json")

# Translate text
chinese_text = "你好世界"
english_result = manager.translate(chinese_text, "zh", "en")
greek_result = manager.translate(chinese_text, "zh", "el")  # Chain translation

# Batch translation
texts = ["你好", "世界", "朋友"]
results = manager.translate_batch(texts, "zh", "en")

# Clear model cache when done
manager.clear_cache()
```

### Interactive Demo
```bash
pipenv run python translate_example.py
```

## Translation Routes

### Direct Routes
- Chinese ↔ English: `Helsinki-NLP/opus-mt-zh-en`, `Helsinki-NLP/opus-mt-en-zh`
- English ↔ Greek: `Helsinki-NLP/opus-mt-en-el`, `Helsinki-NLP/opus-mt-tc-big-el-en`

### Chain Routes (via English)
- Chinese → Greek: Chinese → English → Greek
- Greek → Chinese: Greek → English → Chinese

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

## Examples

### Chinese to Greek (Chain Translation)
```python
manager = TranslationManager()
result = manager.translate("你好，世界！", "zh", "el")
# Output: "Γεια σου, κόσμε!"
```

### Greek to Chinese (Chain Translation)
```python
result = manager.translate("Καλημέρα!", "el", "zh")
# Output: "早上好!"
```

### English to Both
```python
text = "Hello world!"
greek = manager.translate(text, "en", "el")   # "Γεια σου κόσμε!"
chinese = manager.translate(text, "en", "zh")  # "世界好!"
```

## Troubleshooting
- **Model not found**: Check model name in config matches Hugging Face repository
- **Out of memory**: Call `manager.clear_cache()` to free memory
- **Slow performance**: Models are large; first load takes time
- **Authentication errors**: Some models may require Hugging Face authentication
