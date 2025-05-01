"""Basic usage example for README-Gen CLI."""

import os
from pathlib import Path

# This is a sample Python project that would be analyzed
SAMPLE_PROJECT = """
project_root/
├── pyproject.toml
├── README.md
├── sample_package/
│   ├── __init__.py
│   ├── main.py
│   └── utils.py
└── tests/
    ├── __init__.py
    └── test_main.py
"""


def main():
    """Demonstrate how to use README-Gen CLI."""
    print("Example: Generating a README for a Python project")
    print(f"Project structure:\n{SAMPLE_PROJECT}")

    # Setup environment variables
    print("\nStep 1: Set up your environment")
    print("Create a .env file with your OpenAI API key:")
    print("```")
    print("OPENAI_API_KEY=your_openai_api_key_here")
    print("OPENAI_MODEL=gpt-4.1")
    print("```")

    # In a real scenario, you would use the CLI:
    print("\nStep 2: Generate a README")
    print("To generate a README, run:")
    print("readme-gen --output README.md")

    # For a preview without saving:
    print("\nAdditional options:")
    print("To preview without saving:")
    print("readme-gen --preview")

    # With a specific model:
    print("\nTo use a specific LLM model:")
    print("readme-gen --model gpt-4")

    # With a custom env file:
    print("\nTo use a custom environment file:")
    print("readme-gen --env ./my-custom-env")

    print("\nThe CLI will:")
    print("1. Scan your Python project files")
    print("2. Extract docstrings, signatures, and examples")
    print("3. Generate summaries using GPT-4.1 via Agno")
    print("4. Format a complete README.md with badges, TOC, and examples")


if __name__ == "__main__":
    main()
