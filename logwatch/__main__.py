"""Позволяет запускать утилиту как `python -m logwatch`."""

from logwatch.cli.app import app

if __name__ == "__main__":
    app()
