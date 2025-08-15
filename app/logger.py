import logging
import os
from datetime import datetime

def setup_logger(name='translation_api', log_dir='logs'):
    # Check if logger already exists
    logger = logging.getLogger(name)
    if logger.handlers:  # Logger already set up
        return logger
    """Set up logger with both file and console handlers"""
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create formatters
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # File handler
    today = datetime.now().strftime('%Y-%m-%d')
    file_handler = logging.FileHandler(os.path.join(log_dir, f'{today}.log'))
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
