"""Summarizer agent for generating human-friendly descriptions using Agno and LLMs."""

from typing import Dict, List, Optional
import io
import sys
import time
from contextlib import redirect_stdout

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.memory.v2.memory import Memory
from pydantic import BaseModel

from readme_gen.agents.parser import ProjectData, CodeItem
from readme_gen.utils.env import get_openai_api_key, get_openai_model


class Summary(BaseModel):
    """Summary of a code item."""
    item_id: str
    short_description: str
    detailed_description: Optional[str] = None
    usage_examples: List[str] = []


# Global LLM instance to be used by the summarize function
_llm = None


def get_llm(model_name: Optional[str] = None):
    """Get or create a global LLM instance."""
    global _llm
    if _llm is None:
        model = model_name or get_openai_model()
        api_key = get_openai_api_key()
        _llm = OpenAIChat(id=model, api_key=api_key)
    return _llm


def summarize_code(item: CodeItem) -> Summary:
    """Summarize code items using LLMs to generate human-friendly descriptions.

    Args:
        item: CodeItem to summarize

    Returns:
        Summary object with descriptions and examples
    """
    # Create a temporary agent for summarization
    prompt = _build_prompt(item)

    # Create a temporary agent for this specific summarization task
    llm = get_llm()
    summarizer = Agent(
        model=llm,
        instructions=prompt
    )

    # Get response from the agent
    response = summarizer.get_response("Summarize the provided code.")
    response_text = response.content if response else ""

    # Parse the response
    summary = _parse_response(response_text, item.name)
    summary.item_id = item.name

    # Add examples from docstring if available
    if item.examples:
        summary.usage_examples.extend(item.examples)

    return summary


def _build_prompt(item: CodeItem) -> str:
    """Build a prompt for the LLM based on the code item."""
    prompt = f"""You are a technical documentation expert.
    
Given the following Python {item.type}, please provide:
1. A concise one-line description
2. A more detailed explanation of what it does and its purpose
3. A usage example (if possible)

{item.type}: {item.name}
Signature: {item.signature if item.signature else 'N/A'}
Docstring: {item.docstring if item.docstring else 'N/A'}

Format your response like this:
SHORT: <one-line description>
DETAILED: <paragraph explanation>
EXAMPLE: <code example if possible>

Focus on clarity and usefulness for developers."""

    return prompt


def _parse_response(response: str, item_name: str) -> Summary:
    """Parse the LLM response into a Summary object."""
    lines = response.strip().split('\n')

    short_desc = ""
    detailed_desc = ""
    examples = []

    current_section = None
    current_content = []

    for line in lines:
        line = line.strip()
        if line.startswith("SHORT:"):
            if current_section and current_content:
                if current_section == "SHORT":
                    short_desc = "\n".join(current_content).strip()
                elif current_section == "DETAILED":
                    detailed_desc = "\n".join(current_content).strip()
                elif current_section == "EXAMPLE":
                    examples.append("\n".join(current_content).strip())

            current_section = "SHORT"
            current_content = [line.replace("SHORT:", "").strip()]

        elif line.startswith("DETAILED:"):
            if current_section and current_content:
                if current_section == "SHORT":
                    short_desc = "\n".join(current_content).strip()
                elif current_section == "DETAILED":
                    detailed_desc = "\n".join(current_content).strip()
                elif current_section == "EXAMPLE":
                    examples.append("\n".join(current_content).strip())

            current_section = "DETAILED"
            current_content = [line.replace("DETAILED:", "").strip()]

        elif line.startswith("EXAMPLE:"):
            if current_section and current_content:
                if current_section == "SHORT":
                    short_desc = "\n".join(current_content).strip()
                elif current_section == "DETAILED":
                    detailed_desc = "\n".join(current_content).strip()
                elif current_section == "EXAMPLE":
                    examples.append("\n".join(current_content).strip())

            current_section = "EXAMPLE"
            current_content = [line.replace("EXAMPLE:", "").strip()]

        else:
            current_content.append(line)

    # Handle the last section
    if current_section and current_content:
        if current_section == "SHORT":
            short_desc = "\n".join(current_content).strip()
        elif current_section == "DETAILED":
            detailed_desc = "\n".join(current_content).strip()
        elif current_section == "EXAMPLE":
            examples.append("\n".join(current_content).strip())

    # Default short description if empty
    if not short_desc:
        short_desc = f"Python {item_name}"

    return Summary(
        item_id=item_name,
        short_description=short_desc,
        detailed_description=detailed_desc,
        usage_examples=examples,
    )


class SummarizerAgent(Agent):
    """Agent for summarizing Python code items."""

    def __init__(self, memory: Memory, model: Optional[str] = None):
        # Set up the OpenAI model
        model_name = model or get_openai_model()
        api_key = get_openai_api_key()

        print(f"SummarizerAgent: Using model {model_name}")

        llm = OpenAIChat(id=model_name, api_key=api_key)

        # Pass the model to the parent Agent constructor
        super().__init__(
            model=llm,
            memory=memory,
            instructions="You are a technical documentation expert who summarizes Python code items."
        )

    def generate_summaries(self, project_data: ProjectData) -> Dict[str, Summary]:
        """
        Generate summaries for all code items in the project.

        Args:
            project_data: ProjectData containing code items

        Returns:
            Dictionary mapping item IDs to their summaries
        """
        summaries = {}
        total_items = sum(1 for item in project_data.items.values()
                          if item.type in ["module", "class", "function"])

        print(f"Generating summaries for {total_items} items...")
        sys.stdout.flush()

        item_count = 0
        error_count = 0

        # Process items by type - modules first, then classes, then functions
        for item_type in ["module", "class", "function"]:
            for item_id, item in project_data.items.items():
                if item.type == item_type:
                    try:
                        item_count += 1
                        print(
                            f"[{item_count}/{total_items}] Summarizing {item_id}...")
                        sys.stdout.flush()

                        start_time = time.time()

                        # Create a prompt for this specific item
                        prompt = _build_prompt(item)

                        # Use Agent's ask method to get a response
                        response = ""
                        try:
                            # Capture the output from print_response as it prints to stdout
                            output = io.StringIO()
                            with redirect_stdout(output):
                                # Use the built-in print_response method
                                self.print_response(prompt, stream=False)
                            response = output.getvalue()
                        except Exception as api_error:
                            print(f"API error: {str(api_error)}")
                            # Fallback to basic description
                            response = f"SHORT: {item.type.capitalize()}: {item.name}\nDETAILED: {item.docstring if item.docstring else ''}"

                        # Parse the response
                        summary = _parse_response(response, item.name)
                        summary.item_id = item.name

                        # Add examples from docstring if available
                        if item.examples:
                            summary.usage_examples.extend(
                                item.examples)

                        summaries[item_id] = summary

                        if item_count % 10 == 0:
                            print(
                                f"Completed {item_count}/{total_items} summaries.")
                            sys.stdout.flush()

                        end_time = time.time()
                        print(
                            f"Summarizing {item_id} took {end_time - start_time:.2f} seconds")
                    except Exception as e:
                        error_count += 1
                        print(f"Error summarizing {item_id}: {str(e)}")
                        # Create a basic summary as fallback
                        summaries[item_id] = Summary(
                            item_id=item_id,
                            short_description=f"{item.type.capitalize()}: {item.name}",
                        )

        print(
            f"Summary generation complete. {item_count} items processed with {error_count} errors.")
        return summaries
