"""Точка входа CLI на базе Typer."""

import typer
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from logwatch import __version__
from logwatch.core.config import get_settings

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


@app.command()
def config() -> None:
    """Показать текущие настройки (секреты скрыты)."""
    try:
        settings = get_settings()
    except ValidationError as exc:
        console.print(f"[bold red]Ошибка в переменных окружения:[/bold red]\n{exc}")
        raise typer.Exit(code=1) from exc

    table = Table(title="Настройки LogWatch")
    table.add_column("Параметр", style="cyan")
    table.add_column("Значение")
    # SecretStr при выводе автоматически маскируется звёздочками
    for name, value in settings.model_dump().items():
        table.add_row(name, "—" if value is None else str(value))
    table.add_row("telegram_enabled", str(settings.telegram_enabled))
    console.print(table)
