from google.cloud import bigquery
from rich.console import Group
from rich.table import Table
from rich.rule import Rule
from rich.text import Text

from bq_meta import const
from bq_meta.config import Config
from bq_meta.util.num_utils import bytes_fmt, num_fmt


def get_config_info(config: Config) -> Group:
    return Group(text_tuple("Account", config.account))


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
        text_tuple("Table ID", Text(table.full_table_id, style=const.info_style)),
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
