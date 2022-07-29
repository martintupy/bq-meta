from google.cloud import bigquery
from rich.console import Group
from rich.table import Table
from rich.rule import Rule
from rich.text import Text
from rich.columns import Columns
from rich.tree import Tree
from rich.align import Align
from rich.box import SIMPLE

from bq_meta import const
from bq_meta.config import Config
from bq_meta.util import table_utils
from bq_meta.util.num_utils import bytes_fmt, num_fmt

from rich.rule import Rule
from bq_meta import const
from google.cloud import bigquery
from rich.align import Align
from rich.layout import Layout
from rich.console import NewLine
from rich.text import Text
from rich.console import Group
from packaging import version

title = """
██▄ █ ▄▀  ▄▀▄ █ █ ██▀ █▀▄ ▀▄▀   █▄ ▄█ ██▀ ▀█▀ ▄▀▄ █▀▄ ▄▀▄ ▀█▀ ▄▀▄
█▄█ █ ▀▄█ ▀▄█ ▀▄█ █▄▄ █▀▄  █    █ ▀ █ █▄▄  █  █▀█ █▄▀ █▀█  █  █▀█
"""


def header_renderable(config: Config):
    header_title = Align(title, align="center", style=const.info_style)
    header = Layout(name="header", size=4)
    current = version.parse(config.current_version)
    available = version.parse(config.available_version)
    if current < available:
        version_text = Text(f"{current} ► {available}", style=const.darker_style)
    else:
        version_text = Text(f"{current}", style=const.darker_style)
    left = Layout(version_text, size=20)
    mid = Layout(header_title)
    right = Layout(NewLine(), size=20)
    header.split_row(left, mid, right)
    return header


def get_config_info(config: Config) -> Group:
    return Group(text_tuple("Account", config.account))


def get_schema_output(table: bigquery.Table) -> Group:
    schema = table.schema
    tree = Tree(Text("Schema", const.key_style))
    table = Table(box=SIMPLE, show_header=False)
    table_utils.scheme_tree(schema, tree)
    table_utils.scheme_table(schema, table)
    return Group(Rule(style=const.darker_style), Columns([tree, table]))


# fmt: off
def get_table_output(table: bigquery.Table) -> Group:
    size = bytes_fmt(table.num_bytes)
    long_term_size = bytes_fmt(int(table._properties.get("numLongTermBytes", 0)))
    rows = num_fmt(table.num_rows)
    
    created = table.created.strftime("%Y-%m-%d %H:%M:%S UTC")
    modified = table.modified.strftime("%Y-%m-%d %H:%M:%S UTC")
    expiry = table.expires.strftime("%Y-%m-%d %H:%M:%S UTC") if table.expires else None
    
    partitioned_by = table.time_partitioning.type_ if table.time_partitioning else None
    partitioned_field = table.time_partitioning.field if table.time_partitioning else None
    partition_filter = table.require_partition_filter if table.require_partition_filter else None
    _num_partitions = table._properties.get("numPartitions", None)
    num_of_partitions = int(_num_partitions) if _num_partitions else None
    
    streaming_buffer_size = bytes_fmt(table.streaming_buffer.estimated_bytes) if table.streaming_buffer else None
    streaming_buffer_rows = num_fmt(table.streaming_buffer.estimated_rows) if table.streaming_buffer else None
    streaming_entry_time = table.streaming_buffer.oldest_entry_time.strftime("%Y-%m-%d %H:%M:%S UTC") if table.streaming_buffer else None
    return Group(
        Rule(style=const.darker_style),
        text_tuple("Table ID", table.full_table_id),
        text_tuple("Description", table.description),
        text_tuple("Data location", table.location),
        Rule(style=const.darker_style),
        text_tuple("Table size", size),
        text_tuple("Long-term size", long_term_size),
        text_tuple("Number of rows", rows),
        Rule(style=const.darker_style),
        table_tuple({
            "Created": created, 
            "Last modified": modified, 
            "Table expiry": expiry 
        }),
        Rule(style=const.darker_style),
        text_tuple("Partitioned by", partitioned_by),
        text_tuple("Partitioned on field", partitioned_field),
        text_tuple("Partition filter", partition_filter),
        text_tuple("Partitions number", num_of_partitions),
        Rule(style=const.darker_style),
        text_tuple("Clustered by", table.clustering_fields),
        Rule(style=const.darker_style),
        text_tuple("Streaming buffer rows", streaming_buffer_rows),
        text_tuple("Streaming buffer size", streaming_buffer_size),
        text_tuple("Streaming entry time", streaming_entry_time),
        Rule(style=const.darker_style),
    )
# fmt: on


def table_tuple(tuples: dict) -> Text:
    table = Table(
        box=const.equal_box, show_header=False, show_edge=False, pad_edge=False, border_style=const.darker_style
    )
    for key, value in tuples.items():
        text = value if isinstance(tuple, Text) else Text(str(value), style="default")
        table.add_row(Text(key, style=const.key_style), text)
    return table


def text_tuple(name: str, value) -> Text:
    text = None
    if isinstance(value, Text):
        text = value
    else:
        text = Text(str(value), style="default")
    return Text(name, style=const.key_style).append(" = ", style=const.darker_style).append(text)
