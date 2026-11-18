"""Точка входа CLI на базе Typer."""

import typer
from rich.console import Console

from logwatch import __version__

app = typer.Typer(
    name="logwatch",
    help="LogWatch — консольный агрегатор и анализатор логов.",
    no_args_is_help=True,
)
console = Console()


@app.callback()
def main() -> None:
    """LogWatch — консольный агрегатор и анализатор логов."""


@app.command()
def version() -> None:
    """Показать версию утилиты."""
    console.print(f"LogWatch [bold cyan]v{__version__}[/bold cyan]")
