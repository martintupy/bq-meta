from typing import Callable, Iterator
from rich.console import Console

from rich.progress import Progress, TextColumn, TimeElapsedColumn
from rich.text import Text

from bq_meta import const


def progress(console: Console, name: str, iterator: Iterator) -> list:
    size = 0
    result = []
    with Progress(
        TextColumn("[progress.description]{task.description}", style=const.info_style),
        "•",
        TextColumn("[progress.completed]{task.completed}"),
        "•",
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(f"Listing {name}")
        for item in iterator:
            result.append(item)
            progress.advance(task)
            size += 1
    return result


def spinner(console: Console, callable: Callable):
    result = None
    with console.status(Text("Connecting to the API", style=const.darker_style), spinner="point"):
        result = callable()
    return result
