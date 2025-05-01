"""Coordinates the README generation process using Agno agents."""

from pathlib import Path
from typing import Dict, List, Optional

from agno.agent import Agent
from agno.memory.short_term_memory import ShortTermMemory
from agno.tools.base import BaseTool

from readme_gen.agents.parser import ParserAgent
from readme_gen.agents.summarizer import SummarizerAgent
from readme_gen.agents.formatter import FormatterAgent


def generate_readme(
    project_path: Path,
    model: str = "gpt-4",
) -> str:
    """
    Generate a README for a Python project using Agno agents.

    Args:
        project_path: Path to the Python project
        model: LLM model to use for summarization

    Returns:
        String containing the generated README content
    """
    # Create shared memory for agents to communicate
    memory = ShortTermMemory()

    # Initialize agents
    parser = ParserAgent(memory=memory)
    summarizer = SummarizerAgent(memory=memory, model=model)
    formatter = FormatterAgent(memory=memory)

    # Step 1: Parse the project structure
    project_data = parser.parse_project(project_path)
    memory.add("project_data", project_data)

    # Step 2: Generate summaries for modules, classes, functions
    summaries = summarizer.generate_summaries(project_data)
    memory.add("summaries", summaries)

    # Step 3: Format the README with all gathered information
    readme_content = formatter.create_readme(
        project_data=project_data,
        summaries=summaries,
        project_path=project_path,
    )

    return readme_content
