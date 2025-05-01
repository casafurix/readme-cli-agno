"""Parser agent for extracting Python project structure, docstrings, and examples."""

import ast
import inspect
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Set

from agno.agent import Agent
from agno.memory.short_term_memory import ShortTermMemory
from agno.tools.base import BaseTool
from pydantic import BaseModel, Field


class CodeItem(BaseModel):
    """Represents a Python code item (module, class, function)."""
    name: str
    type: str  # "module", "class", or "function"
    docstring: Optional[str] = None
    file_path: Path
    signature: Optional[str] = None
    parent: Optional[str] = None
    children: List[str] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list)


class ProjectData(BaseModel):
    """Represents the structure of a Python project."""
    name: str
    items: Dict[str, CodeItem] = Field(default_factory=dict)
    entry_points: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    root_path: Path


class ParseFileTool(BaseTool):
    """Tool for parsing a Python file."""

    name = "parse_file"
    description = "Parse a Python file to extract classes, functions, docstrings, and examples."

    def run(self, file_path: Path, project_data: ProjectData) -> None:
        """
        Parse a Python file and update the project data.

        Args:
            file_path: Path to the Python file
            project_data: ProjectData to update
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse the file with AST
            module = ast.parse(content)
            module_name = file_path.stem

            # Add module to project data
            relative_path = file_path.relative_to(project_data.root_path)
            module_id = str(relative_path).replace(
                '/', '.').replace('\\', '.').replace('.py', '')

            # Extract module docstring
            module_docstring = ast.get_docstring(module)

            project_data.items[module_id] = CodeItem(
                name=module_id,
                type="module",
                docstring=module_docstring,
                file_path=file_path,
            )

            # Extract classes and functions
            for node in ast.walk(module):
                if isinstance(node, ast.ClassDef):
                    class_id = f"{module_id}.{node.name}"
                    class_docstring = ast.get_docstring(node)

                    project_data.items[class_id] = CodeItem(
                        name=node.name,
                        type="class",
                        docstring=class_docstring,
                        file_path=file_path,
                        parent=module_id,
                        signature=f"class {node.name}",
                    )

                    if module_id in project_data.items:
                        project_data.items[module_id].children.append(class_id)

                    # Extract methods
                    for child_node in node.body:
                        if isinstance(child_node, ast.FunctionDef):
                            method_id = f"{class_id}.{child_node.name}"
                            method_docstring = ast.get_docstring(child_node)

                            # Build signature
                            params = []
                            for param in child_node.args.args:
                                if param.arg != 'self' and param.arg != 'cls':
                                    params.append(param.arg)

                            method_signature = f"def {child_node.name}({', '.join(['self'] + params)})"

                            project_data.items[method_id] = CodeItem(
                                name=child_node.name,
                                type="function",
                                docstring=method_docstring,
                                file_path=file_path,
                                parent=class_id,
                                signature=method_signature,
                            )

                            if class_id in project_data.items:
                                project_data.items[class_id].children.append(
                                    method_id)

                elif isinstance(node, ast.FunctionDef) and node.parent_field != 'body':
                    # Only top-level functions
                    func_id = f"{module_id}.{node.name}"
                    func_docstring = ast.get_docstring(node)

                    # Build signature
                    params = [param.arg for param in node.args.args]
                    func_signature = f"def {node.name}({', '.join(params)})"

                    project_data.items[func_id] = CodeItem(
                        name=node.name,
                        type="function",
                        docstring=func_docstring,
                        file_path=file_path,
                        parent=module_id,
                        signature=func_signature,
                    )

                    if module_id in project_data.items:
                        project_data.items[module_id].children.append(func_id)

            # Look for examples in docstrings
            for item_id, item in project_data.items.items():
                if item.docstring:
                    examples = self._extract_examples(item.docstring)
                    if examples:
                        item.examples.extend(examples)

        except Exception as e:
            # Skip files that can't be parsed
            print(f"Error parsing {file_path}: {str(e)}")

    def _extract_examples(self, docstring: str) -> List[str]:
        """Extract code examples from a docstring."""
        examples = []
        if "example" in docstring.lower() or "examples" in docstring.lower():
            lines = docstring.split('\n')
            in_example = False
            current_example = []

            for line in lines:
                # Check for example section headers or code blocks
                if "example" in line.lower() or line.strip().startswith('>>>'):
                    in_example = True

                if in_example:
                    current_example.append(line)

                # End of example block
                if in_example and line.strip() == '' and current_example:
                    examples.append('\n'.join(current_example))
                    current_example = []
                    in_example = False

            # Catch any remaining example
            if current_example:
                examples.append('\n'.join(current_example))

        return examples


class ParserAgent(Agent):
    """Agent for parsing Python projects."""

    def __init__(self, memory: ShortTermMemory):
        super().__init__(memory=memory)
        self.tools = [ParseFileTool()]

    def parse_project(self, project_path: Path) -> ProjectData:
        """
        Parse a Python project structure.

        Args:
            project_path: Path to the project root

        Returns:
            ProjectData containing the project structure
        """
        # Initialize project data
        project_name = project_path.name
        project_data = ProjectData(
            name=project_name,
            root_path=project_path,
        )

        # Find setup.py or pyproject.toml to extract dependencies
        setup_py = project_path / "setup.py"
        pyproject_toml = project_path / "pyproject.toml"
        requirements_txt = project_path / "requirements.txt"

        if pyproject_toml.exists():
            project_data.dependencies = self._extract_dependencies_from_pyproject(
                pyproject_toml)
        elif setup_py.exists():
            project_data.dependencies = self._extract_dependencies_from_setup(
                setup_py)
        elif requirements_txt.exists():
            project_data.dependencies = self._extract_dependencies_from_requirements(
                requirements_txt)

        # Recursively parse Python files
        python_files = self._find_python_files(project_path)

        for file_path in python_files:
            self.tools[0].run(file_path, project_data)

        return project_data

    def _find_python_files(self, project_path: Path) -> List[Path]:
        """Find all Python files in the project."""
        python_files = []
        exclude_dirs = {"venv", ".venv", "env", ".env", ".git",
                        "__pycache__", "build", "dist", "*.egg-info"}

        for root, dirs, files in os.walk(project_path):
            # Skip excluded directories
            dirs[:] = [
                d for d in dirs if d not in exclude_dirs and not d.startswith('.')]

            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)

        return python_files

    def _extract_dependencies_from_pyproject(self, pyproject_path: Path) -> List[str]:
        """Extract dependencies from pyproject.toml."""
        dependencies = []
        try:
            with open(pyproject_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Very simple parsing - this could be improved with a proper TOML parser
            if "dependencies" in content:
                dep_lines = content.split("dependencies")[1].split(
                    "[")[1].split("]")[0].split("\n")
                for line in dep_lines:
                    line = line.strip().strip('"').strip("'").strip(",")
                    if line and not line.startswith("#"):
                        dependencies.append(line)
        except Exception:
            pass

        return dependencies

    def _extract_dependencies_from_setup(self, setup_path: Path) -> List[str]:
        """Extract dependencies from setup.py."""
        dependencies = []
        try:
            with open(setup_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Very simple parsing - could be improved
            if "install_requires" in content:
                requires_section = content.split("install_requires")[
                    1].split("[")[1].split("]")[0]
                dep_lines = requires_section.split(",")
                for line in dep_lines:
                    line = line.strip().strip('"').strip("'")
                    if line and not line.startswith("#"):
                        dependencies.append(line)
        except Exception:
            pass

        return dependencies

    def _extract_dependencies_from_requirements(self, req_path: Path) -> List[str]:
        """Extract dependencies from requirements.txt."""
        dependencies = []
        try:
            with open(req_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        dependencies.append(line)
        except Exception:
            pass

        return dependencies
