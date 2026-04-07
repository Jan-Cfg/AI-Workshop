"""
Utility Helper Functions
Input validation, logging, and text processing utilities.
"""
import re
import logging
from typing import List, Optional


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def log_message(message: str, level: str = "INFO"):
    """Log a message with specified level."""
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(f"[RAG] {message}")


def validate_query(query: str, min_length: int = 3) -> str:
    """
    Validate user query input.

    Args:
        query: User query
        min_length: Minimum query length

    Raises:
        ValueError: If query is invalid

    Returns:
        Validated query
    """
    if not query or not isinstance(query, str):
        raise ValueError("Query must be a non-empty string")

    query = query.strip()

    if len(query) < min_length:
        raise ValueError(f"Query must be at least {min_length} characters long")

    return query


def validate_document_path(path: str) -> str:
    """
    Validate document file path.

    Args:
        path: File path

    Raises:
        ValueError: If path is invalid

    Returns:
        Validated path
    """
    import os

    if not path or not isinstance(path, str):
        raise ValueError("Path must be a non-empty string")

    if not os.path.exists(path):
        raise ValueError(f"File does not exist: {path}")

    if not os.path.isfile(path):
        raise ValueError(f"Path is not a file: {path}")

    return path


def extract_keywords(text: str, top_k: int = 5) -> List[str]:
    """
    Extract keywords from text (simple word frequency).

    Args:
        text: Input text
        top_k: Number of keywords to extract

    Returns:
        List of keywords
    """
    # Remove special characters and convert to lowercase
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text).lower()

    # Split into words and filter short words
    words = [w for w in text.split() if len(w) > 3]

    # Get unique words and sort by frequency
    word_freq = {}
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1

    keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:top_k]
    return [word for word, _ in keywords]


def format_response(response: str) -> str:
    """
    Format response text for display.

    Args:
        response: Raw response

    Returns:
        Formatted response
    """
    if not response:
        return "No response generated"

    return response.strip()


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """Truncate text to max length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def sanitize_input(user_input: str) -> str:
    """
    Sanitize user input to prevent injection attacks.

    Args:
        user_input: User-provided input

    Returns:
        Sanitized input
    """
    # Remove potentially harmful characters
    sanitized = re.sub(r"[<>\"'`;\\]", "", user_input)
    return sanitized.strip()
