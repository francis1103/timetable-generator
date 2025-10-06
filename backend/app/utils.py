"""
Utility Functions Module

This module contains helper functions that can be used across the application.
Add your utility functions here as needed.
"""

import logging
from datetime import datetime
from typing import Any, Dict


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def log_request(endpoint: str, data: Dict[str, Any]) -> None:
    """
    Log incoming API requests.
    
    Args:
        endpoint (str): The API endpoint being called
        data (dict): The request data
    """
    logger.info(f"Request to {endpoint} at {datetime.now()}")
    logger.debug(f"Request data: {data}")


def log_response(endpoint: str, response: Any, status_code: int = 200) -> None:
    """
    Log API responses.
    
    Args:
        endpoint (str): The API endpoint that was called
        response: The response data
        status_code (int): HTTP status code
    """
    logger.info(f"Response from {endpoint}: Status {status_code}")
    logger.debug(f"Response data: {response}")


def validate_text_input(text: str, min_length: int = 1, max_length: int = 10000) -> bool:
    """
    Validate text input length.
    
    Args:
        text (str): The text to validate
        min_length (int): Minimum allowed length
        max_length (int): Maximum allowed length
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not text or not isinstance(text, str):
        return False
    
    text_length = len(text.strip())
    return min_length <= text_length <= max_length


def format_error_response(error_message: str, error_code: str = "INTERNAL_ERROR") -> Dict[str, str]:
    """
    Format error responses consistently.
    
    Args:
        error_message (str): The error message
        error_code (str): Error code identifier
        
    Returns:
        dict: Formatted error response
    """
    return {
        "error": error_code,
        "message": error_message,
        "timestamp": datetime.now().isoformat()
    }


def sanitize_input(text: str) -> str:
    """
    Sanitize input text by removing potentially harmful characters.
    
    Args:
        text (str): The input text to sanitize
        
    Returns:
        str: Sanitized text
    """
    # Basic sanitization - extend as needed
    sanitized = text.strip()
    return sanitized


# Add more utility functions as needed for your project
