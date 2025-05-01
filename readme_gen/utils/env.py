"""Environment variable handling for README-Gen CLI."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Default model to use if not specified
DEFAULT_MODEL = "gpt-4.1"


def load_env_vars(env_file: Optional[Path] = None) -> None:
    """
    Load environment variables from .env file.

    Args:
        env_file: Optional path to .env file. If None, looks for .env in current directory.
    """
    if env_file and env_file.exists():
        load_dotenv(env_file)
    else:
        # Try to find .env in current directory or parent directories
        load_dotenv()


def get_openai_api_key() -> str:
    """
    Get OpenAI API key from environment variables.

    Returns:
        OpenAI API key

    Raises:
        ValueError: If OPENAI_API_KEY is not set
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY environment variable is not set. "
            "Please set it in your .env file or environment."
        )
    return api_key


def get_openai_model() -> str:
    """
    Get OpenAI model from environment variables, defaulting to gpt-4.1.

    Returns:
        OpenAI model name
    """
    return os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
