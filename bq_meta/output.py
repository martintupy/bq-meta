from rich.console import Group
from rich.text import Text
from rich.rule import Rule

from bq_meta import const
from google.cloud.bigquery import Dataset, Table
from bq_meta.config import Config
from bq_meta.util.num_utils import bytes_fmt, num_fmt
import json


def get_gcloud_info(json: dict) -> Group:
    project = json.get("config", {}).get("project")
    account = json.get("config", {}).get("account")
    return Group(
        Text("Project", style=const.info_style).append(f" = {project}", style="default"),
        Text("Account", style=const.info_style).append(f" = {account}", style="default"),
    )


def get_config_info(config: Config) -> Group:
    return Group(
        Text("Project", style=const.info_style).append(f" = {config.project}", style="default"),
        Text("Account", style=const.info_style).append(f" = {config.account}", style="default"),
    )


# fmt: off
def get_table_output(table: Table) -> Group:
    return Group(
        Text("Table ID", style=const.info_style).append(" = ", style=const.darker_style).append(f"{table.full_table_id}", style="default"),
        Text("Description", style=const.info_style).append(" = ", style=const.darker_style).append(f"{json.dumps(table.description)}", style="default"),
        Text("Data location", style=const.info_style).append(" = ", style=const.darker_style).append(f"{table.location}", style="default"),
        Rule(style=const.border_style),
        Text("Table size", style=const.info_style).append(" = ", style=const.darker_style).append(f"{bytes_fmt(table.num_bytes)}", style="default"),
        Text("Long-term storage size", style=const.info_style).append(f' = {bytes_fmt(int(table._properties.get("numLongTermBytes", "")))}', style="default"),
        Text("Number of rows", style=const.info_style).append(" = ", style=const.darker_style).append(f"{num_fmt(table.num_rows)}", style="default"),
        Rule(style=const.border_style),
        Text("Created", style=const.info_style).append(" = ", style=const.darker_style).append(f'{table.created.strftime("%Y-%m-%d %H:%M:%S")}', style="default"),
        Text("Last modified", style=const.info_style).append(" = ", style=const.darker_style).append(f'{table.modified.strftime("%Y-%m-%d %H:%M:%S")}', style="default"),
        Text("Table expiry", style=const.info_style).append(" = ", style=const.darker_style).append(f"{table.expires}", style="default"),
        Rule(style=const.border_style),
        Text("Partitioned by", style=const.info_style).append(" = ", style=const.darker_style).append(f"{json.dumps(table.time_partitioning.type_)}", style="default"),
        Text("Partitioned on field", style=const.info_style).append(" = ", style=const.darker_style).append(f"{json.dumps(table.time_partitioning.field)}", style="default"),
        Text("Partition filter", style=const.info_style).append(" = ", style=const.darker_style).append(f"{json.dumps(table.require_partition_filter)}", style="default"),
        Rule(style=const.border_style),
        Text("Clustered by", style=const.info_style).append(" = ", style=const.darker_style).append(f"{json.dumps(table.clustering_fields)}", style="default"),
    )
# fmt: on
