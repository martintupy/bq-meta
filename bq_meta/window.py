import webbrowser
from datetime import datetime
from typing import Optional

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
        self.project_id: Optional[str] = None
        self.dataset_id: Optional[str] = None
        self.table_id: Optional[str] = None
        self.table: Optional[bigquery.Table] = None
        self.layout: Layout = Layout()
        self.content: Optional[RenderableType] = None
        self.subtitle = "open (o) | history (h) | quit (q)"
        self.console = console
        self.history_service = history_service
        self.table_service = table_service

    def live_window(self, table: Optional[bigquery.Table]):
        self.table = table
        with Live(self.layout, auto_refresh=False, screen=True, transient=True) as live:
            if self.table:
                self.content = output.get_table_output(self.table)
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

    def _update_table_refs(self):
        """
        Update table identifiers to the state, used dataset (d) and table (t) listing
        """
        if self.table:
            self.project_id = self.table.project
            self.dataset_id = self.table.dataset_id
            self.table_id = self.table.table_id

    def _loop(self, live: Live):
        self._update_panel(live)
        char = readchar.readkey()

        # Open new table
        if char == "o":
            self.table = self.table_service.get_table(live=live)
            if self.table:
                self.subtitle = "open (o) | refresh (r) | schema (s) | console (c) | history (h) | quit (q)"
                self.content = output.get_table_output(self.table)
                self.history_service.save_table(self.table)
            self._update_table_refs()
            self._loop(live)

        # Refresh table
        elif char == "r" and self.table:
            self.table = self.table_service.get_fresh_table(self.table)
            flash_layout(live, self.layout)
            self._loop(live)

        # Show schema
        elif char == "s":
            if self.table:
                self.subtitle = "open (o) | refresh (r) | table (t) | console (c) | history (h) | quit (q)"
                self.content = output.get_schema_output(self.table)
            self._loop(live)

        # Open table in the google console
        elif char == "c":
            if self.table:
                url = f"https://console.cloud.google.com/bigquery?&ws=!1m5!1m4!4m3!1s{self.table.project}!2s{self.table.dataset_id}!3s{self.table.table_id}"
                webbrowser.open(url)
            self._loop(live)

        # Show history
        elif char == "h":
            from_history = self.history_service.pick_table(live)
            if from_history:
                self.table = from_history
                self.subtitle = "open (o) | refresh (r) | schema (s) | console (c) | history (h) | quit (q)"
                self.history_service.save_table(self.table)
                self.content = output.get_table_output(self.table)
                self._update_table_refs()
            self._loop(live)

        # Show table
        elif char == "t":
            if self.table:
                self.subtitle = "open (o) | refresh (r) | schema (s) | console (c) | history (h) | quit (q)"
                self.content = output.get_table_output(self.table)
            self._loop(live)

        # Quit program
        elif char == "q":
            live.stop()

        # Infinite loop, until stopped
        else:
            self._loop(live)
