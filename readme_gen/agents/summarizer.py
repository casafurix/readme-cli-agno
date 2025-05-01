"""Summarizer agent for generating human-friendly descriptions using Agno and LLMs."""

from typing import Dict, List, Optional

from agno.agent import Agent
from agno.llms.openai import OpenAILLM
from agno.memory.short_term_memory import ShortTermMemory
from agno.tools.base import BaseTool
from pydantic import BaseModel

from readme_gen.agents.parser import ProjectData, CodeItem
from readme_gen.utils.env import get_openai_api_key, get_openai_model


class Summary(BaseModel):
    """Summary of a code item."""
    item_id: str
    short_description: str
    detailed_description: Optional[str] = None
    usage_examples: List[str] = []


class SummarizeTool(BaseTool):
    """Tool for summarizing code items using LLMs."""

    name = "summarize_code"
    description = "Summarize code items using LLMs to generate human-friendly descriptions."

    def __init__(self, llm_model: Optional[str] = None):
        super().__init__()
        # Use model provided or get from environment
        model = llm_model or get_openai_model()
        api_key = get_openai_api_key()
        self.llm = OpenAILLM(model=model, api_key=api_key)

    def run(self, item: CodeItem) -> Summary:
        """
        Summarize a code item using LLMs.

        Args:
            item: CodeItem to summarize

        Returns:
            Summary object with descriptions and examples
        """
        prompt = self._build_prompt(item)
        response = self.llm.predict(prompt)

        summary = self._parse_response(response, item.name)
        summary.item_id = item.name

        # Add examples from docstring if available
        if item.examples:
            summary.usage_examples.extend(item.examples)

        return summary

    def _build_prompt(self, item: CodeItem) -> str:
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

    def _parse_response(self, response: str, item_name: str) -> Summary:
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

    def __init__(self, memory: ShortTermMemory, model: Optional[str] = None):
        super().__init__(memory=memory)
        self.tools = [SummarizeTool(llm_model=model)]

    def generate_summaries(self, project_data: ProjectData) -> Dict[str, Summary]:
        """
        Generate summaries for all code items in the project.

        Args:
            project_data: ProjectData containing code items

        Returns:
            Dictionary mapping item IDs to their summaries
        """
        summaries = {}

        # Process items by type - modules first, then classes, then functions
        for item_type in ["module", "class", "function"]:
            for item_id, item in project_data.items.items():
                if item.type == item_type:
                    try:
                        summary = self.tools[0].run(item)
                        summaries[item_id] = summary
                    except Exception as e:
                        print(f"Error summarizing {item_id}: {str(e)}")
                        # Create a basic summary as fallback
                        summaries[item_id] = Summary(
                            item_id=item_id,
                            short_description=f"{item.type.capitalize()}: {item.name}",
                        )

        return summaries
