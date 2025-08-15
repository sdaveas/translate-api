# Translate API Usage

This document explains how to use the Translate API.

## Endpoint

`POST /translate`

### Request Body (JSON)
```
{
  "text": "<text to translate>",
  "dest": "<destination language code>",
  "src": "<source language code or 'auto'>",  // optional, default: 'auto'
  "pronunciation": <true|false>                 // optional, default: false
}
```

- `text` (string): The text you want to translate. **Required**
- `dest` (string): The target language code (e.g., `es` for Spanish). **Required**
- `src` (string): The source language code (e.g., `en` for English) or `'auto'` for auto-detect. Optional.
- `pronunciation` (bool): Whether to include pronunciation in the response. Optional.


### Example Request (curl)

Copy and paste this in your terminal (all on one line or with the backslashes for multi-line):

```sh
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world!",
    "dest": "es",
    "src": "auto",
    "pronunciation": true
  }' \
  http://localhost:5001/translate
```

Or, as a single line (for easy copy-paste):

```sh
curl -X POST -H "Content-Type: application/json" -d '{"text": "Hello world!", "dest": "es", "src": "auto", "pronunciation": true}' http://localhost:5001/translate
```

### Example Response
```
{
  "original_text": "Hello world!",
  "translated_text": "¡Hola Mundo!",
  "source_language": "en",
  "destination_language": "es",
  "detected_language": {
    "code": "en",
    "name": "english"
  },
  "pronunciation": "O-la Mun-do"
}
```

- `original_text`: The original text you sent.
- `translated_text`: The translated text.
- `source_language`: The detected or specified source language code.
- `destination_language`: The target language code.
- `detected_language`: (if auto-detect) An object with `code` and `name`.
- `pronunciation`: (if requested and available) Pronunciation of the translated text.

## List Supported Languages

`GET /languages`

Returns a list of supported languages and their codes.

### Example Response
```
{
  "languages": [
    {"code": "en", "name": "english"},
    {"code": "es", "name": "spanish"},
    ...
  ]
}
```
