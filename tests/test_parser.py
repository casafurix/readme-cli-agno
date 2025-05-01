"""Tests for the parser agent."""

import os
import tempfile
from pathlib import Path

from agno.memory.short_term_memory import ShortTermMemory

from readme_gen.agents.parser import ParserAgent


def test_parser_finds_python_files():
    """Test that the parser can find Python files."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create some Python files
        temp_path = Path(tmp_dir)

        # Create a simple Python module
        module_path = temp_path / "module.py"
        with open(module_path, "w") as f:
            f.write('''"""Test module docstring."""

def test_function():
    """Test function docstring."""
    return True

class TestClass:
    """Test class docstring."""
    
    def test_method(self):
        """Test method docstring."""
        return True
''')

        # Create a directory with a Python file
        os.makedirs(temp_path / "subdir")
        submodule_path = temp_path / "subdir" / "submodule.py"
        with open(submodule_path, "w") as f:
            f.write('''"""Test submodule docstring."""

def sub_function():
    """Test subfunction docstring."""
    return True
''')

        # Initialize the parser
        memory = ShortTermMemory()
        parser = ParserAgent(memory=memory)

        # Parse the project
        project_data = parser.parse_project(temp_path)

        # Check that the modules were found
        assert "module" in project_data.items
        assert "subdir.submodule" in project_data.items

        # Check that the functions were found
        assert "module.test_function" in project_data.items
        assert "subdir.submodule.sub_function" in project_data.items

        # Check that the class was found
        assert "module.TestClass" in project_data.items

        # Check that the method was found
        assert "module.TestClass.test_method" in project_data.items

        # Check that docstrings were extracted
        assert project_data.items["module"].docstring == "Test module docstring."
        assert project_data.items["module.test_function"].docstring == "Test function docstring."
        assert project_data.items["module.TestClass"].docstring == "Test class docstring."
        assert project_data.items["module.TestClass.test_method"].docstring == "Test method docstring."
