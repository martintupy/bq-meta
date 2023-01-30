from enum import Enum
import webbrowser
from datetime import datetime
from typing import Optional
import click

import readchar
from bq_meta import const, output
from bq_meta.config import Config
from bq_meta.service.history_service import HistoryService
from bq_meta.service.table_service import TableService
from google.cloud import bigquery
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich.console import RenderableType
from bq_meta.service.template_service import TemplateService

from bq_meta.util.rich_utils import flash_panel


class View(Enum):
    empty = 1
    table = 2
    schema = 3
    template = 4


class Window:
    def __init__(
        self,
        console: Console,
        config: Config,
        history_service: HistoryService,
        table_service: TableService,
        template_service: TemplateService,
    ):
        self.console = console
        self.config = config
        self.history_service = history_service
        self.table_service = table_service
        self.template_service = template_service
        self.table: Optional[bigquery.Table] = None
        self.project_id: Optional[str] = None
        self.dataset_id: Optional[str] = None
        self.layout: Layout = Layout()
        self.content: Optional[RenderableType] = None
        self.view: View = View.empty
        self.subtitle: Optional[str] = None
        self.template: Optional[str] = None

    def live_window(self, table: Optional[bigquery.Table]):
        if table:
            self._update_table(table)
            self._update_view(View.table)
        else:
            self._update_view(View.empty)

        with Live(self.layout, auto_refresh=False, screen=True, transient=True) as live:
            self._loop(live)

    def _update_panel(self, live: Live) -> None:
        content_layout = Layout()
        header = output.header_layout(self.config)
        if self.content:
            content = Layout(self.content, name="content")
        else:
            content = Layout(name="content", visible=False)
        content_layout.split_column(header, content)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        panel = Panel(
            title=now,
            title_align="right",
            subtitle=self.subtitle,
            renderable=content_layout,
            border_style=const.border_style,
        )
        self.layout = Layout(panel)
        self.panel = panel
        live.update(self.layout, refresh=True)

    def _update_table(self, table: bigquery.Table):
        """
        Update table identifiers to the state, used when listing datasets or tables
        Save table to the history
        """
        if table:
            self.table = table
            self.project_id = table.project
            self.dataset_id = table.dataset_id
            self.history_service.save_table(table)

    def _update_view(self, view: View):
        """
        Set view, subtitle and content
        """
        if view == View.empty:
            self.view = view
            self.subtitle = "open (o) | history (h) | quit (q)"
        elif view == View.table and self.table:
            self.view = view
            self.subtitle = "open (o) | refresh (r) | schema (s) | template (t) | console (c) | history (h) | quit (q)"
            self.content = output.get_table_output(self.table)
        elif view == View.schema and self.table:
            self.view = view
            self.subtitle = "open (o) | refresh (r) | table (s) | console (c) | history (h) | quit (q)"
            self.content = output.get_schema_output(self.table)
        elif view == View.template and self.template:
            self.view = view
            self.subtitle = "open (o) | refresh (r) | schema (s) | table (t) | console (c) | history (h) | quit (q)"
            self.content = output.get_template_output(self.template)

    def _loop(self, live: Live):
        """
        Loop listening on specific keypress, updating live CLI
        """

        self._update_panel(live)
        char = readchar.readkey()
        match char:

            # List projects / Open new table
            case "1" | "o":
                table = self.table_service.get_table(live=live)
                if table:
                    self._update_table(table)
                    self._update_view(View.table)

            # List datasets
            case "2":
                table = self.table_service.get_table(self.project_id, live=live)
                if table:
                    self._update_table(table)
                    self._update_view(View.table)

            # List tables
            case "3":
                table = self.table_service.get_table(self.project_id, self.dataset_id, live=live)
                if table:
                    self._update_table(table)
                    self._update_view(View.table)

            # List history
            case "h":
                table = self.history_service.pick_table(live)
                if table:
                    self._update_table(table)
                    self._update_view(View.table)

            # Refresh view
            case "r" if self.table:
                table = self.table_service.get_fresh_table(self.table)
                flash_panel(live, self.layout, self.panel)
                if table:
                    self.table = table
                    self._update_view(self.view)

            # Toggle schema view
            case "s" if self.table:
                if self.view == View.table:
                    self._update_view(View.schema)
                elif self.view == View.schema:
                    self._update_view(View.table)

            # Open table in the google console
            case "c" if self.table:
                url = f"https://console.cloud.google.com/bigquery?p={self.table.project}&d={self.table.dataset_id}&t={self.table.table_id}&page=query"
                webbrowser.open(url)

            # Toggle template view
            case "t" if self.table:
                if self.view == View.table:
                    template = self.template_service.get_template(live, self.table)
                    if template:
                        self.template = template
                        self._update_view(View.template)
                elif self.view == View.template:
                    self._update_view(View.table)

            # Quit program
            case "q":
                live.stop()
                click.get_current_context().exit()

        # Infinite loop, until quitted (q)
        self._loop(live)
