"""Formatter agent for assembling the final README.md file."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from agno.agent import Agent
from agno.memory.short_term_memory import ShortTermMemory
from agno.tools.base import BaseTool
from pydantic import BaseModel

from readme_gen.agents.parser import ProjectData, CodeItem
from readme_gen.agents.summarizer import Summary
from readme_gen.utils.markdown import generate_badge


class FormatterTool(BaseTool):
    """Tool for formatting README.md content."""

    name = "format_readme"
    description = "Format README.md content with proper Markdown structure."

    def run(
        self,
        project_data: ProjectData,
        summaries: Dict[str, Summary],
        project_path: Path,
    ) -> str:
        """
        Format a README.md file for a Python project.

        Args:
            project_data: ProjectData containing code structure
            summaries: Dictionary of Summaries for code items
            project_path: Path to the project

        Returns:
            String containing the formatted README.md content
        """
        # Get project name and description
        project_name = project_data.name

        # Try to find a top-level module with a docstring for project description
        project_description = ""
        top_modules = [
            item for item_id, item in project_data.items.items()
            if item.type == "module" and "." not in item_id  # No parent module
        ]

        if top_modules and any(module.docstring for module in top_modules):
            for module in top_modules:
                if module.docstring:
                    # Use the first paragraph of the first module docstring
                    project_description = module.docstring.split("\n\n")[0]
                    break

        # If no description found, use the summary of the first module
        if not project_description and top_modules:
            module_id = top_modules[0].name
            if module_id in summaries:
                project_description = summaries[module_id].short_description

        # Build README sections
        sections = []

        # 1. Title and badges
        badges = self._generate_badges(project_data)
        sections.append(
            f"# {project_name}\n\n{' '.join(badges)}\n\n{project_description}")

        # 2. Table of Contents
        toc = self._generate_toc()
        sections.append(toc)

        # 3. Installation
        install = self._generate_installation_section(project_data)
        sections.append(install)

        # 4. Quick Start / Usage
        usage = self._generate_usage_section(project_data, summaries)
        sections.append(usage)

        # 5. API Reference
        api_ref = self._generate_api_reference(project_data, summaries)
        sections.append(api_ref)

        # 6. Examples
        examples = self._generate_examples_section(summaries)
        if examples:
            sections.append(examples)

        # 7. License
        license_text = self._detect_license(project_path)
        if license_text:
            sections.append(license_text)

        # Join all sections
        return "\n\n".join(sections)

    def _generate_badges(self, project_data: ProjectData) -> List[str]:
        """Generate badges for the README."""
        badges = []

        # Python version badge
        badges.append(generate_badge(
            label="python",
            message=">=3.8",
            color="blue",
        ))

        # License badge (default to MIT if not specified)
        badges.append(generate_badge(
            label="license",
            message="MIT",
            color="green",
        ))

        # Add dependency badges for key libraries
        key_libs = ["pytest", "typer", "rich", "pydantic"]
        for dep in project_data.dependencies:
            for lib in key_libs:
                if lib in dep.lower():
                    lib_name = dep.split(">=")[0].split("==")[0].strip()
                    badges.append(generate_badge(
                        label=lib_name,
                        message="✓",
                        color="brightgreen",
                    ))

        return badges

    def _generate_toc(self) -> str:
        """Generate Table of Contents."""
        toc = """## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Examples](#examples)
- [License](#license)
"""
        return toc

    def _generate_installation_section(self, project_data: ProjectData) -> str:
        """Generate Installation section."""
        # Basic pip install instructions
        install = """## Installation

```bash
pip install {}
```

### Dependencies

{}
""".format(
            project_data.name,
            "\n".join(
                f"- `{dep}`" for dep in project_data.dependencies) if project_data.dependencies else "No external dependencies required."
        )

        return install

    def _generate_usage_section(
        self,
        project_data: ProjectData,
        summaries: Dict[str, Summary],
    ) -> str:
        """Generate Usage section."""
        usage = """## Usage

"""
        # Find the main module or entry point
        main_modules = [
            item_id for item_id, item in project_data.items.items()
            if item.type == "module" and "main" in item_id.lower() or "cli" in item_id.lower()
        ]

        if main_modules and main_modules[0] in summaries:
            main_module = main_modules[0]
            summary = summaries[main_module]
            usage += f"{summary.detailed_description}\n\n"

            if summary.usage_examples:
                usage += "### Basic Example\n\n"
                usage += f"```python\n{summary.usage_examples[0]}\n```\n"
        else:
            usage += f"Import and use {project_data.name} in your Python projects:\n\n"
            usage += f"```python\nimport {project_data.name.replace('-', '_')}\n\n# Your code here\n```\n"

        return usage

    def _generate_api_reference(
        self,
        project_data: ProjectData,
        summaries: Dict[str, Summary],
    ) -> str:
        """Generate API Reference section."""
        api_ref = """## API Reference

"""
        # Group by module
        modules = {}
        for item_id, item in project_data.items.items():
            if item.type == "module":
                modules[item_id] = []

        # Add classes and functions to their parent modules
        for item_id, item in project_data.items.items():
            if item.type in ["class", "function"] and item.parent in modules:
                modules[item.parent].append(item_id)

        # Generate reference for each module
        for module_id, children in modules.items():
            if not children:  # Skip empty modules
                continue

            module_name = module_id.split(".")[-1]
            api_ref += f"### {module_name}\n\n"

            if module_id in summaries:
                api_ref += f"{summaries[module_id].short_description}\n\n"

            # Add classes
            classes = [
                child for child in children if project_data.items[child].type == "class"]
            if classes:
                api_ref += "#### Classes\n\n"
                for class_id in classes:
                    class_item = project_data.items[class_id]
                    class_name = class_item.name
                    api_ref += f"##### `{class_name}`\n\n"

                    if class_id in summaries:
                        api_ref += f"{summaries[class_id].detailed_description}\n\n"

                    # Add methods
                    methods = class_item.children
                    if methods:
                        api_ref += "Methods:\n\n"
                        for method_id in methods:
                            method = project_data.items[method_id]
                            api_ref += f"- `{method.signature}`"
                            if method_id in summaries:
                                api_ref += f": {summaries[method_id].short_description}"
                            api_ref += "\n"
                        api_ref += "\n"

            # Add functions
            functions = [
                child for child in children if project_data.items[child].type == "function"]
            if functions:
                api_ref += "#### Functions\n\n"
                for func_id in functions:
                    func = project_data.items[func_id]
                    api_ref += f"##### `{func.signature}`\n\n"

                    if func_id in summaries:
                        api_ref += f"{summaries[func_id].detailed_description}\n\n"

        return api_ref

    def _generate_examples_section(self, summaries: Dict[str, Summary]) -> str:
        """Generate Examples section."""
        all_examples = []
        for item_id, summary in summaries.items():
            if summary.usage_examples:
                all_examples.extend(summary.usage_examples)

        if not all_examples:
            return ""

        examples = """## Examples

"""
        for i, example in enumerate(all_examples[:3]):  # Limit to 3 examples
            examples += f"### Example {i+1}\n\n```python\n{example}\n```\n\n"

        return examples

    def _detect_license(self, project_path: Path) -> str:
        """Detect license and return license section."""
        license_files = ["LICENSE", "LICENSE.txt", "LICENSE.md"]
        license_type = None

        for filename in license_files:
            license_path = project_path / filename
            if license_path.exists():
                try:
                    with open(license_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip().lower()
                        if "mit" in content:
                            license_type = "MIT"
                        elif "apache" in content:
                            license_type = "Apache"
                        elif "gnu" in content or "gpl" in content:
                            license_type = "GPL"
                        else:
                            license_type = "See LICENSE file"
                except Exception:
                    pass

        if not license_type:
            license_type = "MIT"  # Default

        return f"## License\n\n{license_type}"


class FormatterAgent(Agent):
    """Agent for formatting README.md files."""

    def __init__(self, memory: ShortTermMemory):
        super().__init__(memory=memory)
        self.tools = [FormatterTool()]

    def create_readme(
        self,
        project_data: ProjectData,
        summaries: Dict[str, Summary],
        project_path: Path,
    ) -> str:
        """
        Create a README.md file for a Python project.

        Args:
            project_data: ProjectData containing code structure
            summaries: Dictionary of Summaries for code items
            project_path: Path to the project

        Returns:
            String containing the README.md content
        """
        readme_content = self.tools[0].run(
            project_data=project_data,
            summaries=summaries,
            project_path=project_path,
        )

        return readme_content
