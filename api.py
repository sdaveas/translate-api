"""
FastAPI service for the Translation API.
Provides REST endpoints for translating text between Chinese, English, and Greek.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import logging
from translation_manager import TranslationManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Translation API",
    description="API for translating text between Chinese, English, and Greek",
    version="1.0.0"
)

# Add CORS middleware to allow browser requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize translation manager (singleton)
translation_manager = None

def get_translation_manager():
    """Get or create the translation manager singleton."""
    global translation_manager
    if translation_manager is None:
        logger.info("Initializing Translation Manager...")
        translation_manager = TranslationManager()
    return translation_manager


# Pydantic models for request/response
class TranslationRequest(BaseModel):
    """Request model for translation endpoint."""
    from_lang: str = Field(..., alias="from", description="Source language code (zh, en, el)")
    to_lang: str = Field(..., alias="to", description="Target language code (zh, en, el)")
    text: str = Field(..., description="Text to translate")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "from": "zh",
                "to": "el",
                "text": "你好，世界！"
            }
        }


class TranslationResponse(BaseModel):
    """Response model for translation endpoint."""
    original_text: str = Field(..., description="Original text")
    translated_text: str = Field(..., description="Translated text")
    from_lang: str = Field(..., alias="from", description="Source language code")
    to_lang: str = Field(..., alias="to", description="Target language code")
    translation_path: Optional[List[str]] = Field(None, description="Translation path (for chain translations)")
    
    class Config:
        populate_by_name = True


class BatchTranslationRequest(BaseModel):
    """Request model for batch translation endpoint."""
    from_lang: str = Field(..., alias="from", description="Source language code (zh, en, el)")
    to_lang: str = Field(..., alias="to", description="Target language code (zh, en, el)")
    texts: List[str] = Field(..., description="List of texts to translate")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "from": "en",
                "to": "zh",
                "texts": ["Hello", "World", "How are you?"]
            }
        }


class BatchTranslationResponse(BaseModel):
    """Response model for batch translation endpoint."""
    translations: List[TranslationResponse] = Field(..., description="List of translation results")
    from_lang: str = Field(..., alias="from", description="Source language code")
    to_lang: str = Field(..., alias="to", description="Target language code")
    
    class Config:
        populate_by_name = True


class LanguageInfo(BaseModel):
    """Information about available languages and routes."""
    languages: dict = Field(..., description="Available languages with their codes")
    routes: dict = Field(..., description="Available translation routes")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    message: str = Field(..., description="Status message")


# API Endpoints

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - returns service information."""
    return HealthResponse(
        status="ok",
        message="Translation API is running. Visit /docs for API documentation."
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="ok", message="Service is healthy")


@app.get("/languages", response_model=LanguageInfo)
async def get_languages():
    """Get information about available languages and translation routes."""
    manager = get_translation_manager()
    return LanguageInfo(
        languages=manager.config.get("language_names", {}),
        routes=manager.get_available_routes()
    )


@app.post("/translate", response_model=TranslationResponse)
async def translate(request: TranslationRequest):
    """
    Translate text from one language to another.
    
    Supports:
    - Direct translation when models are available
    - Chain translation through intermediate languages
    
    Language codes:
    - zh: Chinese
    - en: English  
    - el: Greek
    """
    # Validate language codes
    valid_langs = ["zh", "en", "el"]
    if request.from_lang not in valid_langs:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid source language: {request.from_lang}. Must be one of: {', '.join(valid_langs)}"
        )
    if request.to_lang not in valid_langs:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid target language: {request.to_lang}. Must be one of: {', '.join(valid_langs)}"
        )
    if request.from_lang == request.to_lang:
        raise HTTPException(
            status_code=400,
            detail="Source and target languages cannot be the same"
        )
    
    try:
        manager = get_translation_manager()
        
        # Get translation route to determine path
        route = manager.get_translation_route(request.from_lang, request.to_lang)
        if not route:
            raise HTTPException(
                status_code=400,
                detail=f"No translation route available from {request.from_lang} to {request.to_lang}"
            )
        
        # Perform translation
        translated_text = manager.translate(
            request.text,
            request.from_lang,
            request.to_lang
        )
        
        # Build translation path for response
        translation_path = None
        if len(route["path"]) > 1:
            # Chain translation
            path_names = []
            for step in route["path"]:
                parts = step.split("-")
                path_names.append(manager.config["language_names"].get(parts[0], parts[0]))
            path_names.append(manager.config["language_names"].get(request.to_lang, request.to_lang))
            translation_path = path_names
        
        return TranslationResponse(
            original_text=request.text,
            translated_text=translated_text,
            from_lang=request.from_lang,
            to_lang=request.to_lang,
            translation_path=translation_path
        )
        
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@app.post("/translate/batch", response_model=BatchTranslationResponse)
async def translate_batch(request: BatchTranslationRequest):
    """
    Translate multiple texts at once.
    
    More efficient than calling /translate multiple times as models
    are loaded once and reused for all translations.
    """
    # Validate language codes
    valid_langs = ["zh", "en", "el"]
    if request.from_lang not in valid_langs:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid source language: {request.from_lang}. Must be one of: {', '.join(valid_langs)}"
        )
    if request.to_lang not in valid_langs:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid target language: {request.to_lang}. Must be one of: {', '.join(valid_langs)}"
        )
    if request.from_lang == request.to_lang:
        raise HTTPException(
            status_code=400,
            detail="Source and target languages cannot be the same"
        )
    
    try:
        manager = get_translation_manager()
        
        # Get translation route
        route = manager.get_translation_route(request.from_lang, request.to_lang)
        if not route:
            raise HTTPException(
                status_code=400,
                detail=f"No translation route available from {request.from_lang} to {request.to_lang}"
            )
        
        # Build translation path
        translation_path = None
        if len(route["path"]) > 1:
            path_names = []
            for step in route["path"]:
                parts = step.split("-")
                path_names.append(manager.config["language_names"].get(parts[0], parts[0]))
            path_names.append(manager.config["language_names"].get(request.to_lang, request.to_lang))
            translation_path = path_names
        
        # Translate all texts
        translations = []
        for text in request.texts:
            translated = manager.translate(text, request.from_lang, request.to_lang)
            translations.append(TranslationResponse(
                original_text=text,
                translated_text=translated,
                from_lang=request.from_lang,
                to_lang=request.to_lang,
                translation_path=translation_path
            ))
        
        return BatchTranslationResponse(
            translations=translations,
            from_lang=request.from_lang,
            to_lang=request.to_lang
        )
        
    except Exception as e:
        logger.error(f"Batch translation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch translation failed: {str(e)}")


@app.delete("/cache")
async def clear_cache():
    """
    Clear the model cache to free memory.
    
    Useful when running low on memory or switching between many language pairs.
    Next translation will be slower as models need to be reloaded.
    """
    try:
        manager = get_translation_manager()
        manager.clear_cache()
        return {"status": "ok", "message": "Model cache cleared successfully"}
    except Exception as e:
        logger.error(f"Cache clear error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
