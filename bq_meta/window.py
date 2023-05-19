import webbrowser
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional

import click
import pyperclip
import readchar
from google.cloud import bigquery
from readchar import key
from rich.console import Console, RenderableType
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel

from bq_meta import const, output
from bq_meta.config import Config
from bq_meta.service.history_service import HistoryService
from bq_meta.service.table_service import TableService
from bq_meta.service.snippet_service import SnippetService
from bq_meta.util import bash_util
from bq_meta.util.rich_utils import flash_panel


class View(Enum):
    empty = 1
    table = 2
    schema = 3
    snippets = 4


@dataclass
class Hint:
    key: str
    name: str


hint_open = Hint("o", "Open new table")
hint_refresh = Hint("r", "Refresh table")
hint_table = Hint("t", "Show table")
hint_schema = Hint("s", "Show schema")
hint_snippets = Hint("p", "Show snippets")
hint_console = Hint("c", "Open in console")
hint_history = Hint("h", "Show history")
hint_quit = Hint("q", "Quit")

all_hints = [hint_open, hint_refresh, hint_table, hint_schema, hint_snippets, hint_console, hint_history]


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
        match self.view:
            case View.empty:
                self.hints = [hint_open, hint_history]
            case View.table if self.table:
                self.hints = all_hints
                self.values = []
                self.selected_value = None
                self.content = output.get_table_output(self.table)
                self._update_table(self.table)
            case View.schema if self.table:
                self.hints = all_hints
                self.values = []
                self.selected_value = None
                live.stop()
                with self.console.pager():
                    self.console.print(output.get_schema_output(self.table))
                self.view = View.table
                live.start()
            case View.snippets if self.table:
                self.hints = all_hints
                self.snippet = self.snippet_service.get_snippet(self.selected_value, self.table)
                self.content = output.get_snippet_output(self.snippet)

    def _update_panel(self, live: Live) -> None:
        window_layout = Layout(name="window")
        body_layout = Layout(name="body")
        hints_layout = output.hints_layout(self.hints, self.bottom_hints)
        content_layout = output.content_layout(self.content)
        list_layout = output.list_layout(self.values, self.selected_value)
        header_layout = output.header_layout(self.config)
        body_layout.split_row(hints_layout, content_layout, list_layout)
        window_layout.split_column(header_layout, body_layout)
        self.panel = Panel(
            title=self.now.strftime("%Y-%m-%d %H:%M:%S UTC"),
            title_align="right",
            renderable=window_layout,
            border_style=const.border_style,
        )
        self.layout = Layout(self.panel)
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
                self.view = View.table
                self.selected_value = None

            case key.UP if self.values and self.selected_value:
                idx = max([0, self.values.index(self.selected_value) - 1])
                self.selected_value = self.values[idx]

            case key.DOWN if self.values and self.selected_value:
                idx = min([len(self.values) - 1, self.values.index(self.selected_value) + 1])
                self.selected_value = self.values[idx]

            # List projects / Open new table
            case "1" | "o":
                self.view = View.table
                self.table = self.table_service.get_table(live=live)

            # List datasets
            case "2":
                table = self.table_service.get_table(self.project_id, live=live)
                if table:
                    self.view = View.table
                    self.table = table

            # List tables
            case "3":
                table = self.table_service.get_table(self.project_id, self.dataset_id, live=live)
                if table:
                    self.view = View.table
                    self.table = table

            # List history
            case "h":
                table = self.history_service.pick_table(live)
                if table:
                    self.view = View.table
                    self.table = table

            # Refresh content
            case "r" if self.table:
                flash_panel(live, self.layout, self.panel)
                self.now = datetime.utcnow()
                self.table = self.table_service.get_fresh_table(self.table)

            # Show schema view
            case "s" if self.table:
                self.view = View.schema

            # Open google console
            case "c" if self.table:
                match self.view:
                    case View.snippets:
                        url = f"https://console.cloud.google.com/bigquery?p={self.table.project}&d={self.table.dataset_id}&t={self.table.table_id}"
                        pyperclip.copy(self.snippet)
                        webbrowser.open(url)

                    case _:
                        url = f"https://console.cloud.google.com/bigquery?p={self.table.project}&d={self.table.dataset_id}&t={self.table.table_id}&page=table"
                        webbrowser.open(url)

            # Show snippets view
            case "p" if self.table:
                self.view = View.snippets
                snippets = self.snippet_service.list_snippets()
                self.values = snippets
                self.selected_value = snippets[0] if snippets else None

            # Quit program
            case "q":
                live.stop()
                click.get_current_context().exit()

        # Infinite loop, until quitted (q)
        self._loop(live)
