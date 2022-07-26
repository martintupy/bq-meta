import json
import time
import webbrowser
from datetime import datetime
from typing import List, Optional

import readchar
from bq_meta import const, output
from google.cloud.bigquery import Client
from google.cloud.bigquery.table import TableReference
from bq_meta.config import Config
from bq_meta.service.history_service import HistoryService
from bq_meta.service.project_service import ProjectService
from bq_meta.util import bash_util
from google.cloud import bigquery
from google.cloud.bigquery.schema import SchemaField
from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.console import Group
from rich.text import Text
from rich.tree import Tree

from bq_meta.util.rich_utils import progress


class MetaService:
    def __init__(
        self,
        console: Console,
        config: Config,
        client: Client,
        project_service: ProjectService,
        history_service: HistoryService,
    ):
        self.console = console
        self.config = config
        self.client = client
        self.project_service = project_service
        self.history_service = history_service

    # ======================   Get   =======================

    def get_dataset(self, project_id: Optional[str], dataset_id: Optional[str]) -> bigquery.Dataset:
        project_id = project_id if project_id else self.pick_project_id()
        dataset_id = dataset_id if dataset_id else self.pick_dataset_id(project_id)
        dataset = self.client.get_dataset(f"{project_id}.{dataset_id}")
        return dataset

    def get_table(
        self, project_id: Optional[str], dataset_id: Optional[str], table_id: Optional[str]
    ) -> bigquery.Table:
        project_id = project_id if project_id else self.pick_project_id()
        dataset_id = dataset_id if dataset_id else self.pick_dataset_id(project_id)
        table_id = table_id if table_id else self.pick_table_id(project_id, dataset_id)
        table = self.client.get_table(f"{project_id}.{dataset_id}.{table_id}")
        return table

    def get_table_panel(self, table_output: Group) -> Panel:
        group = Group(output.header_renderable, table_output)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        panel = Panel(
            title=now,
            title_align="right",
            subtitle="refresh (r) | new (n) | schema (s) | console (c) | history (h) | quit (q)",
            renderable=group,
            border_style=const.border_style,
        )
        return panel

    # ======================  Print  ======================

    def print_table(
        self,
        project_id: Optional[str] = None,
        dataset_id: Optional[str] = None,
        table_id: Optional[str] = None,
        raw: bool = False,
    ):
        table = self.get_table(project_id, dataset_id, table_id)
        if raw:
            self.print_table_raw(table)
        else:
            self.print_table_rich(table)
        self.history_service.save_one(table)  # save sucessfuly printed table

    def print_table_raw(self, table: bigquery.Table):
        properties = json.dumps(table._properties, indent=2)
        self.console.print_json(properties)

    def print_table_rich(self, table: bigquery.Table):
        def loop(table: bigquery.Table, table_output: Group, live: Live):
            char = readchar.readchar()
            if char == "r":
                table = self.get_table(table.project, table.dataset_id, table.table_id)
                table_output = output.get_table_output(table)
                panel = self.get_table_panel(table_output)
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                panel.title = now
                live.update(panel, refresh=True)
                panel.border_style = const.request_style  # border will flash a short period of time
                live.update(panel, refresh=True)
                time.sleep(0.1)
                panel.border_style = const.border_style
                live.update(panel, refresh=True)
                loop(table, table_output, live)
            elif char == "n":  # Open new table
                live.stop()
                self.print_table()
            elif char == "s":  # Quit program, print metadata and schema
                live.stop()
                schema = self.get_schema_renderable(table)
                self.console.print(Group(table_output, schema))
            elif char == "c":  # Open table in the google console
                live.stop()
                url = f"https://console.cloud.google.com/bigquery?&ws=!1m5!1m4!4m3!1s{table.project}!2s{table.dataset_id}!3s{table.table_id}"
                url_output = Text("Opened browser").append(f": {url}")
                self.console.print(table_output)
                self.console.print(url_output)
                webbrowser.open(url)
            elif char == "h":  # Show history
                live.stop()
                from_history = self.history_service.pick_one()
                table_ref = TableReference.from_string(from_history.replace(":", "."))
                project_id = table_ref.project
                dataset_id = table_ref.dataset_id
                table_id = table_ref.table_id
                self.print_table(project_id, dataset_id, table_id)
            elif char == "q":  # Quit program, print metadata
                live.stop()
                self.console.print(table_output)
            else:
                loop(table, table_output, live)

        table_output = output.get_table_output(table)
        panel = self.get_table_panel(table_output)
        with Live(panel, auto_refresh=False, screen=True) as live:
            loop(table, table_output, live)

    # ======================   Pick   ======================

    def pick_project_id(self) -> Optional[str]:
        project_ids = self.project_service.list_projects()
        return bash_util.pick_one(project_ids, self.console)

    def pick_dataset_id(self, project_id: str) -> Optional[str]:
        dataset_ids = []
        iterator = self.client.list_datasets(project=project_id)
        for dataset in progress(self.console, "datasets", iterator):
            dataset_ids.append(dataset.dataset_id)
        return bash_util.pick_one(dataset_ids, self.console)

    def pick_table_id(self, project_id: str, dataset_id: str) -> Optional[str]:
        table_ids = []
        iterator = self.client.list_tables(f"{project_id}.{dataset_id}")
        for table in progress(self.console, "tables", iterator):
            table_ids.append(table.table_id)
        return bash_util.pick_one(table_ids, self.console)

    # ======================  Schema  ======================

    def get_schema_renderable(self, table: bigquery.Table):
        schema = table.schema
        tree = Tree(Text("Schema", const.key_style))
        table = Table(box=box.SIMPLE, show_header=False)
        MetaService._scheme_tree(schema, tree)
        MetaService._scheme_table(schema, table)
        return Columns([tree, table])

    def _scheme_table(schema: List[SchemaField], table: Table):
        for field in schema:
            table.add_row(field.field_type, field.mode)
            if field.field_type == "RECORD":
                MetaService._scheme_table(field.fields, table)
        return

    def _scheme_tree(fields: List[SchemaField], tree: Tree):
        for field in fields:
            node = tree.add(Text(f"{field.name}"))
            if field.field_type == "RECORD":
                MetaService._scheme_tree(field.fields, node)
        return
