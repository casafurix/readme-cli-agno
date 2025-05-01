"""Coordinates the README generation process using Agno agents."""

import sys
from pathlib import Path
from typing import Dict, List

from agno.agent import Agent
from agno.memory.v2.memory import Memory
from agno.models.openai import OpenAIChat

from readme_gen.agents.parser import ParserAgent
from readme_gen.agents.summarizer import SummarizerAgent
from readme_gen.agents.formatter import FormatterAgent
from readme_gen.utils.env import get_openai_api_key, get_openai_model


def generate_readme(
    project_path: Path,
) -> str:
    """
    Generate a README for a Python project using Agno agents.

    Args:
        project_path: Path to the Python project

    Returns:
        String containing the generated README content
    """
    # Get model from environment
    model_name = get_openai_model()
    api_key = get_openai_api_key()

    print(f"Initializing with model: {model_name}")

    # Initialize model and set it for the summarizer
    model = OpenAIChat(id=model_name, api_key=api_key)

    # Create shared memory for agents to communicate
    memory = Memory(model=model)
    memory_data = {}

    # Initialize agents
    print("Initializing parser agent...")
    parser = ParserAgent(memory=memory)

    print("Initializing summarizer agent...")
    summarizer = SummarizerAgent(memory=memory, model=model_name)

    print("Initializing formatter agent...")
    formatter = FormatterAgent(memory=memory)

    # Step 1: Parse the project structure
    print("Step 1: Parsing project structure...")
    sys.stdout.flush()
    project_data = parser.parse_project(project_path)
    memory_data["project_data"] = project_data
    print("Project parsing complete.")

    # Step 2: Generate summaries for modules, classes, functions
    print("Step 2: Generating summaries...")
    sys.stdout.flush()
    summaries = summarizer.generate_summaries(project_data)
    memory_data["summaries"] = summaries
    print("Summary generation complete.")

    # Step 3: Format the README with all gathered information
    print("Step 3: Formatting README...")
    sys.stdout.flush()
    readme_content = formatter.create_readme(
        project_data=project_data,
        summaries=summaries,
        project_path=project_path,
    )
    print("README formatting complete.")

    return readme_content
