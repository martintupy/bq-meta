import json
from typing import List

from bq_meta import const
from google.cloud import bigquery
from google.cloud.bigquery.schema import SchemaField
from rich import box
from rich.columns import Columns
from rich.table import Table
from rich.text import Text
from rich.tree import Tree


def get_schema(table: bigquery.Table):
    schema = table.schema
    tree = Tree(Text("Schema", const.key_style))
    table = Table(box=box.SIMPLE, show_header=False)
    _scheme_tree(schema, tree)
    _scheme_table(schema, table)
    return Columns([tree, table])


def _scheme_table(schema: List[SchemaField], table: Table):
    for field in schema:
        table.add_row(field.field_type, field.mode)
        if field.field_type == "RECORD":
            _scheme_table(field.fields, table)
    return


def _scheme_tree(fields: List[SchemaField], tree: Tree):
    for field in fields:
        node = tree.add(Text(f"{field.name}"))
        if field.field_type == "RECORD":
            _scheme_tree(field.fields, node)
    return


def get_properties(table: bigquery.Table) -> str:
    return json.dumps(table._properties, indent=2)
