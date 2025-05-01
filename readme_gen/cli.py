"""Command-line interface for README-Gen."""

import os
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from readme_gen.agents.coordinator import generate_readme
from readme_gen.utils.env import load_env_vars, get_openai_model

# Load environment variables on module import
load_env_vars()

app = typer.Typer(
    help="Generate comprehensive README files for Python projects using Agno agents."
)
console = Console()


@app.command()
def main(
    path: Optional[Path] = typer.Argument(
        ".",
        help="Path to the Python project directory",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
    output: Path = typer.Option(
        "README.md",
        "--output",
        "-o",
        help="Output file path for the generated README",
    ),
    preview: bool = typer.Option(
        False,
        "--preview",
        "-p",
        help="Preview the README in terminal without saving",
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model",
        "-m",
        help="The LLM model to use for summarization (overrides OPENAI_MODEL env variable)",
    ),
    env_file: Optional[Path] = typer.Option(
        None,
        "--env",
        "-e",
        help="Path to .env file with OpenAI API key and model",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
):
    """
    Generate a comprehensive README.md file for your Python project.

    The tool scans your project's code, extracts docstrings, signatures, and examples,
    then uses Agno agents to create a well-structured README document automatically.
    """
    # Load environment from specified file if provided
    if env_file:
        load_env_vars(env_file)

    # If model is specified in CLI, set it in environment
    if model:
        os.environ["OPENAI_MODEL"] = model

    # Get the model we're using for the display message
    selected_model = get_openai_model()

    abs_path = path.absolute()
    console.print(
        f"[bold green]Analyzing Python project at[/] [bold cyan]{abs_path}[/]")
    console.print(f"[dim]Using model:[/] [cyan]{selected_model}[/]")

    try:
        readme_content = generate_readme(
            project_path=abs_path,
        )

        if preview:
            console.print("\n[bold]README Preview:[/]\n")
            console.print(readme_content)
            console.print("\n[italic]Preview only - not saving to file[/]")
        else:
            # Determine output filename based on whether README.md already exists
            output_path = abs_path / output

            # If output file already exists and is README.md, use README_AGNO.md instead
            if output_path.exists() and output_path.name.lower() == "readme.md":
                # Get the stem (filename without extension) and extension
                stem = output_path.stem
                suffix = output_path.suffix
                # Create new filename with _AGNO appended before the extension
                new_filename = f"{stem}_AGNO{suffix}"
                output_path = abs_path / new_filename
                console.print(
                    f"[yellow]README.md already exists. Using {new_filename} instead.[/]")

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(readme_content)
            console.print(
                f"\n[bold green]README successfully generated at[/] [bold cyan]{output_path}[/]")

    except Exception as e:
        console.print(f"[bold red]Error generating README:[/] {str(e)}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
