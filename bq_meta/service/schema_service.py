from typing import List

from bq_meta import const, Config
from bq_meta.bq_client import BqClient
from bq_meta.util import bash_util
from google.cloud.bigquery.schema import SchemaField
from google.cloud import bigquery
from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.tree import Tree


class SchemaService:
    def __init__(self, console: Console, config: Config, bq_client: BqClient):
        self.console = console
        self.config = config
        self.bq_client = bq_client

    def pick_dataset(self):
        datasets = []
        for dataset in self.bq_client.client.list_datasets(self.config.project):
            datasets.append(dataset.dataset_id)
        return next(iter(bash_util.fzf(datasets)), None)

    def get_table(self) -> bigquery.Table:
        dataset = self.pick_dataset()
        tables = list(self.bq_client.client.list_tables(dataset))
        table_ids = [table.table_id for table in tables]
        table_id = next(iter(bash_util.fzf(table_ids)), None)
        table_list_item = next(table for table in tables if table.table_id == table_id)
        return self.bq_client.client.get_table(table_list_item)

    def get_schema(self):
        bq_table = self.get_table()
        schema = bq_table.schema
        tree = Tree(Text(bq_table.full_table_id, style=const.info_style))
        table = Table(box=box.SIMPLE, show_header=False)
        SchemaService._scheme_table(schema, table)
        SchemaService._scheme_tree(schema, tree)
        return Columns([tree, table])

    def _scheme_table(schema: List[SchemaField], table: Table):
        for field in schema:
            table.add_row(field.field_type, field.mode)
            if field.field_type == "RECORD":
                SchemaService._scheme_table(field.fields, table)
        return

    def _scheme_tree(fields: List[SchemaField], tree: Tree):
        for field in fields:
            node = tree.add(Text(f"{field.name}"))
            if field.field_type == "RECORD":
                SchemaService._scheme_tree(field.fields, node)
        return
