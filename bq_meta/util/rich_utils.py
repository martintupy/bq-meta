from threading import Event
from typing import Iterator
from rich.console import Console

from rich.progress import Progress, TextColumn, TimeElapsedColumn
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout

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
        task = progress.add_task(f"Fetching {name}")
        for item in iterator:
            result.append(item)
            progress.advance(task)
            size += 1
    return result


def flash_panel(live: Live, layout: Layout, panel: Panel):
    event = Event()
    panel.border_style = const.request_style  # border will flash a short period of time
    live.update(layout, refresh=True)
    event.wait(0.1)
    if not event.is_set():
        panel.border_style = const.border_style
        live.update(layout, refresh=True)
