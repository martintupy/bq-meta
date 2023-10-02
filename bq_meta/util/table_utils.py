import json
from typing import List

from google.cloud import bigquery
from google.cloud.bigquery.schema import SchemaField
from rich.table import Table
from rich.text import Text
from rich.tree import Tree


def scheme_table(schema: List[SchemaField], table: Table):
    for field in schema:
        table.add_row(field.field_type, field.mode)
        if field.field_type == "RECORD":
            scheme_table(field.fields, table)
    return


def scheme_tree(schema: List[SchemaField], tree: Tree):
    for field in schema:
        node = tree.add(Text(f"{field.name}"))
        if field.field_type == "RECORD":
            scheme_tree(field.fields, node)
    return


def get_properties(table: bigquery.Table) -> str:
    return json.dumps(table._properties, indent=2)


def get_schema_json(table: bigquery.Table) -> str:
    return json.dumps(table._properties.get("schema", {}).get("fields", {}))


def get_table_link(table: bigquery.Table) -> str:
    return f"https://console.cloud.google.com/bigquery?p={table.project}&d={table.dataset_id}&t={table.table_id}&page=table"
