import webbrowser
from datetime import datetime
from typing import List, Optional

import readchar
from bq_meta import const, output
from bq_meta.bq_client import BqClient
from bq_meta.config import Config
from bq_meta.service.project_service import ProjectService
from bq_meta.util import bash_util
from google.cloud.bigquery import Dataset, Table
from google.cloud.bigquery.schema import SchemaField
from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree


class MetaService:
    def __init__(self, console: Console, config: Config, bq_client: BqClient, project_service: ProjectService):
        self.console = console
        self.config = config
        self.bq_client = bq_client
        self.project_service = project_service

    def get_dataset(self, project_id: Optional[str], dataset_id: Optional[str]) -> Dataset:
        project_id = project_id if project_id else self.pick_project_id()
        dataset_id = dataset_id if dataset_id else self.pick_dataset_id(project_id)
        dataset = self.bq_client.client.get_dataset(f"{project_id}.{dataset_id}")
        return dataset

    def get_table(self, project_id: Optional[str], dataset_id: Optional[str], table_id: Optional[str]) -> Table:
        project_id = project_id if project_id else self.pick_project_id()
        dataset_id = dataset_id if dataset_id else self.pick_dataset_id(project_id)
        table_id = table_id if table_id else self.pick_table_id(project_id, dataset_id)
        table = self.bq_client.client.get_table(f"{project_id}.{dataset_id}.{table_id}")
        return table

    def get_table_renderable(self, table: Table) -> Panel:
        group = output.get_table_output(table)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        panel = Panel(
            title=Text(now, style=const.time_style),
            title_align="right",
            subtitle="refresh (r) / open (o) / schema (s)",
            renderable=group,
            border_style=const.border_style,
        )
        return panel

    def print_table_meta(self, project_id: Optional[str], dataset_id: Optional[str], table_id: Optional[str]):
        def loop(table: Table, panel: Panel, live: Live):
            char = readchar.readchar()
            if char == "r":
                table = self.get_table(table.project, table.dataset_id, table.table_id)
                panel = self.get_table_renderable(table)
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                panel.title = now
                live.update(panel, refresh=True)
                loop(table, panel, live)
            elif char == "o":
                live.stop()
                url = f"https://console.cloud.google.com/bigquery?&ws=!1m5!1m4!4m3!1s{table.project}!2s{table.dataset_id}!3s{table.table_id}"
                panel = Panel(
                    Text("Opened browser", style=const.info_style).append(f": {url}", style=const.link_style),
                    border_style=const.border_style,
                )
                self.console.print(panel)
                webbrowser.open(url)
            elif char == "s":
                live.stop()
                self.print_schema(table.project, table.dataset_id, table.table_id)
            else:
                return

        table = self.get_table(project_id, dataset_id, table_id)
        panel = self.get_table_renderable(table)
        with Live(panel, auto_refresh=False) as live:
            loop(table, panel, live)

    def pick_project_id(self) -> Optional[str]:
        project_ids = self.project_service.list_projects()
        return bash_util.pick_one(project_ids, self.console)

    def pick_dataset_id(self, project_id: str) -> Optional[str]:
        dataset_ids = []
        datasets = list(self.bq_client.client.list_datasets(project=project_id))
        for dataset in datasets:
            dataset_ids.append(dataset.dataset_id)
        return bash_util.pick_one(dataset_ids, self.console)

    def pick_table_id(self, project_id: str, dataset_id: str) -> Optional[str]:
        table_ids = []
        tables = list(self.bq_client.client.list_tables(f"{project_id}.{dataset_id}"))
        for table in tables:
            table_ids.append(table.table_id)
        return bash_util.pick_one(table_ids, self.console)

    def get_schema_renderable(self, project_id: Optional[str], dataset_id: Optional[str], table_id: Optional[str]):
        table = self.get_table(project_id, dataset_id, table_id)
        schema = table.schema
        tree = Tree(Text(table.full_table_id, style=const.info_style))
        table = Table(box=box.SIMPLE, show_header=False)
        MetaService._scheme_tree(schema, tree)
        MetaService._scheme_table(schema, table)
        return Columns([tree, table])

    def print_schema(self, project_id: Optional[str], dataset_id: Optional[str], table_id: Optional[str]):
        schema = self.get_schema_renderable(project_id, dataset_id, table_id)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        panel = Panel(
            title=now,
            title_align="right",
            renderable=schema,
            border_style=const.border_style,
        )
        self.console.print(panel)

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
