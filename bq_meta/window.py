import webbrowser
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional

import click
import pyperclip
import readchar
from google.cloud import bigquery
from loguru import logger
from readchar import key
from rich.console import Console, RenderableType
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel

from bq_meta import const, output
from bq_meta.config import Config
from bq_meta.service.history_service import HistoryService
from bq_meta.service.snippet_service import SnippetService
from bq_meta.service.table_service import TableService
from bq_meta.util import bash_util, table_utils
from bq_meta.util.rich_utils import flash_content, flash_panel


class View(Enum):
    empty = 1
    table = 2
    schema = 3
    snippets = 4
    metadata = 5


class Metadata(Enum):
    table_id = 1
    link = 2
    schema = 3


@dataclass
class Hint:
    key: str
    name: str


hint_open = Hint("o", "Open new table")
hint_table = Hint("t", "Show table")
hint_schema = Hint("s", "Show schema")
hint_snippets = Hint("p", "Show snippets")
hint_metadata = Hint("c", "Show metadata")
hint_history = Hint("h", "Show history")
hint_open_browser = Hint("b", "Open in browser")

hint_refresh = Hint("r", "Refresh")
hint_copy = Hint("c", "Copy")
hint_quit = Hint("q", "Quit")

all_hints = [
    hint_open,
    hint_open_browser,
    hint_table,
    hint_schema,
    hint_snippets,
    hint_metadata,
    hint_history,
]


class Window:
    def __init__(
        self,
        console: Console,
        config: Config,
        history_service: HistoryService,
        table_service: TableService,
        snippet_service: SnippetService,
    ):
        self.console = console
        self.config = config
        self.history_service = history_service
        self.table_service = table_service
        self.snippet_service = snippet_service
        self.table: Optional[bigquery.Table] = None
        self.project_id: Optional[str] = None
        self.dataset_id: Optional[str] = None
        self.layout: Layout = Layout()
        self.content: Optional[RenderableType] = None
        self.view: View = View.empty
        self.hints: List[str] = []
        self.bottom_hints: List[str] = [hint_quit]
        self.values: List[str] = []
        self.selected_value: Optional[str] = None
        self.snippet: Optional[str] = None

    def live_window(self, table: Optional[bigquery.Table]):
        self.now = datetime.utcnow()
        self.table = table
        with Live(self.layout, auto_refresh=False, screen=True, transient=True) as live:
            self._loop(live)

    def _update_content(self, live: Live):
        logger.trace("Updated content")
        match self.view:
            case View.empty:
                self.hints = [hint_open, hint_history]
            case View.table if self.table:
                self.hints = all_hints
                self.bottom_hints = [hint_refresh, hint_quit]
                self.content = output.get_table_output(self.table)
                self._update_table(self.table)
            case View.schema if self.table:
                live.stop()
                with self.console.pager():
                    self.console.print(output.get_schema_output(self.table))
                self.view = View.table
                live.start()
            case View.snippets if self.table:
                self.hints = all_hints
                self.bottom_hints = [hint_refresh, hint_copy, hint_quit]
                self.content = self.snippet_service.get_snippet(self.selected_value, self.table)
            case View.metadata if self.table:
                self.hints = all_hints
                self.bottom_hints = [hint_refresh, hint_copy, hint_quit]
                if self.selected_value == Metadata.table_id.name:
                    self.content = self.table.full_table_id
                elif self.selected_value == Metadata.link.name:
                    self.content = table_utils.get_table_link(self.table)
                elif self.selected_value == Metadata.schema.name:
                    self.content = table_utils.get_schema_json(self.table)

    def _update_panel(self, live: Live) -> None:
        window_layout = Layout(name="window")
        body_layout = Layout(name="body")
        hints_layout = output.hints_layout(self.hints, self.bottom_hints)
        self.content_panel = output.content_panel(self.content)
        content_layout = Layout(self.content_panel, name="content")
        list_layout = output.list_layout(self.values, self.selected_value)
        header_layout = output.header_layout(self.config)
        body_layout.split_row(hints_layout, content_layout, list_layout)
        window_layout.split_column(header_layout, body_layout)
        self.window_panel = output.window_panel(window_layout, self.now)
        self.layout = Layout(self.window_panel)
        live.update(self.layout, refresh=True)

    def _update_table(self, table: Optional[bigquery.Table]):
        """
        Update table identifiers to the state, save table to the history
        """
        if table:
            self.table = table
            self.project_id = table.project
            self.dataset_id = table.dataset_id
            self.history_service.save_table(table)

    def _loop(self, live: Live):
        """
        Loop listening on specific keypress, updating live CLI
        """
        self._update_content(live)
        self._update_panel(live)
        char = readchar.readkey()
        match char:
            case "t" | key.BACKSPACE | key.ESC:
                logger.trace("Table view")
                self.view = View.table
                self.values = []
                self.selected_value = None

            case key.UP if self.values and self.selected_value:
                idx = max([0, self.values.index(self.selected_value) - 1])
                self.selected_value = self.values[idx]

            case key.DOWN if self.values and self.selected_value:
                idx = min([len(self.values) - 1, self.values.index(self.selected_value) + 1])
                self.selected_value = self.values[idx]

            # List projects / Open new table
            case "1" | "o":
                logger.trace(f"Pressed 'o' ({hint_open.name})")
                self.view = View.table
                self.table = self.table_service.get_table(live=live)

            # List datasets
            case "2":
                logger.trace("Pressed '2' (List datasets)")
                table = self.table_service.get_table(self.project_id, live=live)
                if table:
                    self.view = View.table
                    self.table = table

            # List tables
            case "3":
                logger.trace("Pressed '3' (List tables)")
                table = self.table_service.get_table(self.project_id, self.dataset_id, live=live)
                if table:
                    self.view = View.table
                    self.table = table

            # List history
            case "h":
                logger.trace(f"Pressed 'h' ({hint_history.name})")
                table = self.history_service.pick_table(live)
                if table:
                    self.view = View.table
                    self.table = table

            # Refresh content
            case "r" if self.table:
                logger.trace(f"Pressed 'r' ({hint_refresh.name})")
                flash_panel(live, self.layout, self.window_panel)
                self.now = datetime.utcnow()
                self.table = self.table_service.get_fresh_table(self.table)

            # Show schema view
            case "s" if self.table:
                logger.trace(f"Pressed 's' ({hint_schema.name})")
                self.values = []
                self.view = View.schema

            # Open in browser
            case "b" if self.table:
                logger.trace(f"Pressed 'b' ({hint_open_browser.name})")
                url = f"https://console.cloud.google.com/bigquery?p={self.table.project}&d={self.table.dataset_id}&t={self.table.table_id}&page=table"
                webbrowser.open(url)

            # Copy
            case "c" if self.table and self.view in [View.metadata, View.snippets]:
                logger.trace(f"Pressed 'c' ({hint_copy.name})")
                flash_content(live, self.layout, self.content_panel)
                pyperclip.copy(self.content)

            # Copy table
            case "c" if self.table and self.view == View.table:
                logger.trace(f"Pressed 'c' ({hint_copy.name})")
                flash_content(live, self.layout, self.content_panel)
                pyperclip.copy(table_utils.get_properties(self.table))

            # Show metadata
            case "m" if self.table:
                logger.trace(f"Pressed 'm' ({hint_metadata.name})")
                self.view = View.metadata
                self.values = [Metadata.table_id.name, Metadata.link.name, Metadata.schema.name]
                self.selected_value = Metadata.table_id.name

            # Show snippets view
            case "p" if self.table:
                logger.trace(f"Pressed 'p' ({hint_snippets.name})")
                self.view = View.snippets
                snippets = self.snippet_service.list_snippets()
                self.values = snippets
                self.selected_value = snippets[0] if snippets else None

            # Quit
            case "q":
                logger.trace(f"Pressed 'q' ({hint_quit.name})")
                live.stop()
                click.get_current_context().exit()

        # Infinite loop, until quitted (q)
        self._loop(live)
