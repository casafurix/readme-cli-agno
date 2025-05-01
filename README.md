# README-Gen CLI

A command-line tool that automatically generates comprehensive README files for Python projects using Agno agents.

## Features

- Scans Python projects to extract code structure, docstrings, and usage examples
- Auto-generates complete README.md with proper sections (Installation, Usage, API Reference, Examples)
- Uses Agno agents for parsing, summarization, and formatting
- Includes badges, table of contents, and code snippets automatically
- Zero configuration required
- Uses GPT-4.1 by default for high-quality summaries

## Installation

```bash
pip install readme-gen-cli
```

## Quick Start

1. Set up your OpenAI API key:

```bash
# Create a .env file in your project directory
echo "OPENAI_API_KEY=your_key_here" > .env
echo "OPENAI_MODEL=gpt-4.1" >> .env
```

2. Generate your README:

```bash
# Navigate to your Python project's root directory
cd your-python-project

# Generate a README file
readme-gen --output README.md
```

## Environment Variables

README-Gen supports configuration through environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: The OpenAI model to use (defaults to `gpt-4.1`)

You can:

- Set these directly in your environment
- Create a `.env` file in your project directory
- Specify a custom env file with `--env your-env-file`

## CLI Options

```bash
# Preview without saving to a file
readme-gen --preview

# Use a different model
readme-gen --model gpt-4

# Specify a custom .env file
readme-gen --env ./my-env-file
```

## How It Works

README-Gen uses three Agno agents to generate your documentation:

1. **Parser Agent**: Traverses your project's file tree to extract module/class/function signatures and docstrings
2. **Summarizer Agent**: Uses LLMs to craft human-friendly descriptions based on your code
3. **Formatter Agent**: Assembles a beautiful Markdown document with proper formatting

## License

MIT
