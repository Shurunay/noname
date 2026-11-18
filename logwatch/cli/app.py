"""Точка входа CLI на базе Typer."""

import typer
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from logwatch import __version__
from logwatch.core.config import get_settings
from logwatch.core.logger import get_logger, setup_logging

app = typer.Typer(
    name="logwatch",
    help="LogWatch — консольный агрегатор и анализатор логов.",
    no_args_is_help=True,
)
console = Console()
logger = get_logger("cli")


@app.callback()
def main(ctx: typer.Context) -> None:
    """LogWatch — консольный агрегатор и анализатор логов."""
    try:
        settings = get_settings()
    except ValidationError as exc:
        # Логирование ещё не настроено — сообщаем об ошибке напрямую
        console.print(f"[bold red]Ошибка в переменных окружения:[/bold red]\n{exc}")
        raise typer.Exit(code=1) from exc

    setup_logging(settings)
    logger.info("Запуск команды: %s", ctx.invoked_subcommand)


@app.command()
def version() -> None:
    """Показать версию утилиты."""
    console.print(f"LogWatch [bold cyan]v{__version__}[/bold cyan]")


@app.command()
def config() -> None:
    """Показать текущие настройки (секреты скрыты)."""
    settings = get_settings()
    table = Table(title="Настройки LogWatch")
    table.add_column("Параметр", style="cyan")
    table.add_column("Значение")
    # SecretStr при выводе автоматически маскируется звёздочками
    for name, value in settings.model_dump().items():
        table.add_row(name, "—" if value is None else str(value))
    table.add_row("telegram_enabled", str(settings.telegram_enabled))
    console.print(table)
    logger.debug("Выведено %d параметров настроек", len(table.rows))
