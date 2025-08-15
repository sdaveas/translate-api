"""
Translation Manager for handling multi-language translations with configurable routing.
Supports direct and chain translations between Chinese, English, and Greek.
"""

import json
import torch
import os
import sys
from typing import Dict, List, Optional, Tuple
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logger import setup_logger

# Set up logging
logger = setup_logger('translation_api')


class TranslationManager:
    """Manages translation between multiple languages with configurable routing."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize the TranslationManager with configuration.
        
        Args:
            config_path: Path to the JSON configuration file
        """
        # Use default config path if not provided
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "translation_config.json")
        self.config = self._load_config(config_path)
        self.pipelines = {}  # Cache for loaded translation pipelines
        self.models = {}  # Cache for loaded models
        self.tokenizers = {}  # Cache for loaded tokenizers
        
        # Determine device
        if self.config.get("device", "auto") == "auto":
            if torch.backends.mps.is_available():
                self.device = "mps"
            elif torch.cuda.is_available():
                self.device = "cuda"
            else:
                self.device = "cpu"
        else:
            self.device = self.config["device"]
        
        logger.info(f"Using device: {self.device}")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file {config_path} not found!")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing configuration file: {e}")
            raise
    
    def _get_pipeline(self, model_name: str) -> pipeline:
        """
        Get or create a translation pipeline for the specified model.
        
        Args:
            model_name: HuggingFace model identifier
            
        Returns:
            Translation pipeline
        """
        if model_name not in self.pipelines:
            logger.info(f"Loading model: {model_name}")
            device_arg = 0 if self.device == "cuda" else -1 if self.device == "cpu" else self.device
            self.pipelines[model_name] = pipeline(
                "translation", 
                model=model_name,
                device=device_arg
            )
        return self.pipelines[model_name]
    
    def _get_model_and_tokenizer(self, model_name: str) -> Tuple:
        """
        Get or load model and tokenizer (alternative to pipeline).
        
        Args:
            model_name: HuggingFace model identifier
            
        Returns:
            Tuple of (tokenizer, model)
        """
        if model_name not in self.models:
            logger.info(f"Loading model and tokenizer: {model_name}")
            self.tokenizers[model_name] = AutoTokenizer.from_pretrained(model_name)
            self.models[model_name] = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            
            # Move model to appropriate device
            if self.device == "cuda":
                self.models[model_name] = self.models[model_name].cuda()
            elif self.device == "mps":
                self.models[model_name] = self.models[model_name].to("mps")
                
        return self.tokenizers[model_name], self.models[model_name]
    
    def get_translation_route(self, source_lang: str, target_lang: str) -> Optional[Dict]:
        """
        Get the translation route configuration for a language pair.
        
        Args:
            source_lang: Source language code (e.g., 'zh', 'en', 'el')
            target_lang: Target language code
            
        Returns:
            Route configuration dict or None if not available
        """
        routes = self.config.get("translation_routes", {})
        if source_lang in routes and target_lang in routes[source_lang]:
            return routes[source_lang][target_lang]
        return None
    
    def translate(self, text: str, source_lang: str, target_lang: str, 
                 use_pipeline: bool = True) -> str:
        """
        Translate text from source language to target language.
        
        Args:
            text: Text to translate
            source_lang: Source language code (e.g., 'zh', 'en', 'el')
            target_lang: Target language code
            use_pipeline: Whether to use pipeline API (True) or direct model API (False)
            
        Returns:
            Translated text
            
        Raises:
            ValueError: If translation route is not available
        """
        # Get translation route
        route = self.get_translation_route(source_lang, target_lang)
        if not route:
            raise ValueError(
                f"No translation route available from "
                f"{self.config['language_names'].get(source_lang, source_lang)} to "
                f"{self.config['language_names'].get(target_lang, target_lang)}"
            )
        
        # Log the translation path
        path_description = " → ".join([
            self.config['language_names'].get(p.split('-')[0], p.split('-')[0])
            for p in route['path']
        ])
        if len(route['path']) > 1:
            path_description += f" → {self.config['language_names'].get(target_lang, target_lang)}"
        else:
            path_description = (
                f"{self.config['language_names'].get(source_lang, source_lang)} → "
                f"{self.config['language_names'].get(target_lang, target_lang)}"
            )
        
        logger.info(f"Translation path: {path_description}")
        
        # Perform translation(s)
        current_text = text
        for model_name in route['models']:
            if use_pipeline:
                translator = self._get_pipeline(model_name)
                # Add generation parameters to prevent repetition
                result = translator(
                    current_text, 
                    max_length=512,
                    num_beams=4,
                    early_stopping=True,
                    no_repeat_ngram_size=3,
                    length_penalty=2.0,
                    temperature=1.0
                )
                current_text = result[0]['translation_text']
            else:
                tokenizer, model = self._get_model_and_tokenizer(model_name)
                inputs = tokenizer(current_text, return_tensors="pt", padding=True, max_length=512, truncation=True)
                
                # Move inputs to device
                if self.device == "cuda":
                    inputs = {k: v.cuda() for k, v in inputs.items()}
                elif self.device == "mps":
                    inputs = {k: v.to("mps") for k, v in inputs.items()}
                
                # Generate with parameters to prevent repetition
                outputs = model.generate(
                    **inputs,
                    max_length=512,
                    num_beams=4,
                    early_stopping=True,
                    no_repeat_ngram_size=3,
                    length_penalty=2.0,
                    temperature=1.0,
                    do_sample=False
                )
                current_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            logger.info(f"After {model_name}: {current_text[:100]}...")
        
        return current_text
    
    def translate_batch(self, texts: List[str], source_lang: str, 
                       target_lang: str, use_pipeline: bool = True) -> List[str]:
        """
        Translate multiple texts in batch.
        
        Args:
            texts: List of texts to translate
            source_lang: Source language code
            target_lang: Target language code
            use_pipeline: Whether to use pipeline API
            
        Returns:
            List of translated texts
        """
        return [
            self.translate(text, source_lang, target_lang, use_pipeline)
            for text in texts
        ]
    
    def get_available_routes(self) -> Dict[str, List[str]]:
        """
        Get all available translation routes.
        
        Returns:
            Dictionary mapping source languages to available target languages
        """
        routes = self.config.get("translation_routes", {})
        available = {}
        for source_lang, targets in routes.items():
            source_name = self.config['language_names'].get(source_lang, source_lang)
            available[source_name] = []
            for target_lang in targets.keys():
                target_name = self.config['language_names'].get(target_lang, target_lang)
                available[source_name].append(target_name)
        return available
    
    def clear_cache(self):
        """Clear all cached models and pipelines to free memory."""
        self.pipelines.clear()
        self.models.clear()
        self.tokenizers.clear()
        logger.info("Model cache cleared")
