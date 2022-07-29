import webbrowser
from datetime import datetime
from typing import Optional
import click

import readchar
from bq_meta import const, output
from bq_meta.service.history_service import HistoryService
from bq_meta.service.table_service import TableService
from google.cloud import bigquery
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich.console import Group, RenderableType

from bq_meta.util.rich_utils import flash_layout


class Window:
    def __init__(
        self,
        console: Console,
        history_service: HistoryService,
        table_service: TableService,
    ):
        self.table: Optional[bigquery.Table] = None
        self.project_id: Optional[str] = None
        self.dataset_id: Optional[str] = None
        self.layout: Layout = Layout()
        self.content: Optional[RenderableType] = None
        self.subtitle = "open (o) | history (h) | quit (q)"
        self.console = console
        self.history_service = history_service
        self.table_service = table_service

    def live_window(self, table: Optional[bigquery.Table]):
        if table:
            self._update_table(table)
        with Live(self.layout, auto_refresh=False, screen=True, transient=True) as live:
            self._loop(live)

    def _update_panel(self, live: Live) -> None:
        if self.content:
            group = Group(output.header_renderable, self.content)
        else:
            group = Group(output.header_renderable)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        panel = Panel(
            title=now,
            title_align="right",
            subtitle=self.subtitle,
            renderable=group,
            border_style=const.border_style,
        )
        self.layout = Layout(panel)
        live.update(self.layout, refresh=True)

    def _update_table(self, table: bigquery.Table):
        """
        Update table identifiers to the state, used when listing dataset and tables
        Update subtitle for table view
        Save table to history
        Set content to table output
        """
        self.table = table
        self.project_id = table.project
        self.dataset_id = table.dataset_id
        self.subtitle = "open (o) | refresh (r) | schema (s) | console (c) | history (h) | quit (q)"
        self.history_service.save_table(self.table)
        self.content = output.get_table_output(self.table)

    def _loop(self, live: Live):
        self._update_panel(live)
        char = readchar.readkey()

        # List projects / Open new table
        if char == "1" or char == "o":
            table = self.table_service.get_table(live=live)
            if table:
                self._update_table(table)

        # List datasets
        elif char == "2":
            table = self.table_service.get_table(self.project_id, live=live)
            if table:
                self._update_table(table)

        # List tables
        elif char == "3":
            table = self.table_service.get_table(self.project_id, self.dataset_id, live=live)
            if table:
                self._update_table(table)

        # List history
        elif char == "h":
            table = self.history_service.pick_table(live)
            if table:
                self._update_table(table)

        # Refresh table
        elif char == "r" and self.table:
            self.table = self.table_service.get_fresh_table(self.table)
            flash_layout(live, self.layout)

        # Show schema
        elif char == "s":
            if self.table:
                self.subtitle = "open (o) | refresh (r) | table (t) | console (c) | history (h) | quit (q)"
                self.content = output.get_schema_output(self.table)

        # Show table
        elif char == "t":
            if self.table:
                self.subtitle = "open (o) | refresh (r) | schema (s) | console (c) | history (h) | quit (q)"
                self.content = output.get_table_output(self.table)

        # Open table in the google console
        elif char == "c":
            if self.table:
                url = f"https://console.cloud.google.com/bigquery?&ws=!1m5!1m4!4m3!1s{self.table.project}!2s{self.table.dataset_id}!3s{self.table.table_id}"
                webbrowser.open(url)

        # Quit program
        elif char == "q":
            live.stop()
            click.get_current_context().exit()

        # Infinite loop, until quitted (q)
        self._loop(live)
