import webbrowser
from datetime import datetime
from typing import Optional

import readchar
from readchar import key
from bq_meta import const, output
from bq_meta.service.history_service import HistoryService
from bq_meta.service.table_service import TableService
from google.cloud import bigquery
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.console import Group, RenderableType

from bq_meta.util import table_utils
from bq_meta.util.rich_utils import flash_panel


class Window:
    def __init__(
        self,
        console: Console,
        history_service: HistoryService,
        table_service: TableService,
    ):
        self.table: bigquery.Table = None
        self.panel: Panel = None
        self.console = console
        self.history_service = history_service
        self.table_service = table_service

    def live_window(self, table: Optional[bigquery.Table]):
        self.table = table
        with Live(self.panel, auto_refresh=False, screen=True, transient=True) as live:
            if self.table:
                table_content = output.get_table_output(self.table)
                self.update_panel(live, table_content)
            else:
                self.update_panel(live, None)
            self.loop(live)

    def update_panel(self, live: Live, content: Optional[RenderableType]) -> None:
        group = Group(output.header_renderable)
        if content:
            group = Group(output.header_renderable, content)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.panel = Panel(
            title=now,
            title_align="right",
            subtitle="open (o) | refresh (r) | schema (s) | console (c) | history (h) | quit (q)",
            renderable=group,
            border_style=const.border_style,
        )
        live.update(self.panel, refresh=True)

    def loop(self, live: Live):
        char = readchar.readkey()

        # Open new table
        if char == "o":
            self.table = self.table_service.get_table()
            table_content = output.get_table_output(self.table) if self.table else None
            self.update_panel(live, table_content)
            self.loop(live)

        # Refresh table
        elif (char == "r" or char == key.ESC) and self.table:
            self.table = self.table_service.get_fresh_table(self.table)
            table_content = output.get_table_output(self.table)
            self.update_panel(live, table_content)
            flash_panel(live, self.panel)
            self.loop(live)

        # Show schema of current table
        elif char == "s":
            schema_content = table_utils.get_schema(self.table) if self.table else None
            self.update_panel(live, schema_content)
            self.loop(live)

        # Open table in the google console
        elif char == "c":
            if self.table:
                url = f"https://console.cloud.google.com/bigquery?&ws=!1m5!1m4!4m3!1s{self.table.project}!2s{self.table.dataset_id}!3s{self.table.table_id}"
                webbrowser.open(url)
            self.loop(live)

        # Show history
        elif char == "h":
            self.table = self.history_service.pick_table()
            table_content = output.get_table_output(self.table) if self.table else None
            self.update_panel(live, table_content)
            self.loop(live)

        # Quit program
        elif char == "q":
            live.stop()

        # Infinite loop, until stopped
        else:
            self.loop(live)
