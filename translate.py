from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# Option 1: Using pipeline (easier)
print("Loading translation model...")
translator = pipeline("translation", model="Helsinki-NLP/opus-mt-zh-en")

# Text to translate from Chinese to English
text_to_translate = "你好，世界！今天天气很好。"

print(f"Original text (Chinese): {text_to_translate}")

# Perform translation
translation = translator(text_to_translate)
print(f"Translated text (English): {translation[0]['translation_text']}")

# Option 2: Using tokenizer and model directly (more control)
print("\n--- Alternative method using tokenizer and model directly ---")
tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-zh-en")
model = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-zh-en")

# Tokenize the input text
inputs = tokenizer(text_to_translate, return_tensors="pt", padding=True)

# Generate translation
outputs = model.generate(**inputs)

# Decode the output
translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(f"Translated text (using direct method): {translated_text}")
