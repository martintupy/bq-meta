
from google.cloud.bigquery import Table
from rich.console import Group
from rich.rule import Rule
from rich.text import Text

from bq_meta import const
from bq_meta.config import Config
from bq_meta.util.num_utils import bytes_fmt, num_fmt


def get_config_info(config: Config) -> Group:
    return Group(
        text_tuple("Project", config.project),
        text_tuple("Account", config.account),
    )


# fmt: off
def get_table_output(table: Table) -> Group:
    size = bytes_fmt(table.num_bytes)
    long_term_size = bytes_fmt(int(table._properties.get("numLongTermBytes", "")))
    rows = num_fmt(table.num_rows)
    created = table.created.strftime("%Y-%m-%d %H:%M:%S")
    modified = table.modified.strftime("%Y-%m-%d %H:%M:%S")
    expiry = table.expires.strftime("%Y-%m-%d %H:%M:%S") if table.expires else ""
    return Group(
        text_tuple("Table ID", table.full_table_id),
        text_tuple("Description", table.description),
        text_tuple("Data location", table.location),
        Rule(style=const.border_style),
        text_tuple("Table size", size),
        text_tuple("Long-term storage size", long_term_size),
        text_tuple("Number of rows", rows),
        Rule(style=const.border_style),
        text_tuple("Created", created),
        text_tuple("Last modified", modified),
        text_tuple("Table expiry", expiry),
        Rule(style=const.border_style),
        text_tuple("Partitioned by", table.time_partitioning.type_),
        text_tuple("Partitioned on field", table.time_partitioning.field),
        text_tuple("Partition filter", table.require_partition_filter),
        Rule(style=const.border_style),
        text_tuple("Clustered by", table.clustering_fields),
    )
# fmt: on


def text_tuple(name: str, value) -> Text:
    return (
        Text(name, style=const.info_style).append(" = ", style=const.darker_style).append(str(value), style="default")
    )
