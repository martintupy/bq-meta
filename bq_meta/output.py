from datetime import datetime
from google.cloud.bigquery import Table
from rich.console import Group
from rich.rule import Rule
from rich.text import Text
import json

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
    # print(json.dumps(table._properties))
    size = bytes_fmt(table.num_bytes)
    long_term_size = bytes_fmt(int(table._properties.get("numLongTermBytes", "")))
    rows = num_fmt(table.num_rows)
    
    created = table.created.strftime("%Y-%m-%d %H:%M:%S")
    modified = table.modified.strftime("%Y-%m-%d %H:%M:%S")
    expiry = table.expires.strftime("%Y-%m-%d %H:%M:%S") if table.expires else ""
    
    partitioned_by = table.time_partitioning.type_ if table.time_partitioning else ""
    partitioned_field = table.time_partitioning.field if table.time_partitioning else ""
    partition_filter = table.require_partition_filter if table.require_partition_filter else ""
    _num_partitions = table._properties.get("numPartitions", None)
    num_of_partitions = int(_num_partitions) if _num_partitions else None
    
    streaming_buffer_size = bytes_fmt(table.streaming_buffer.estimated_bytes) if table.streaming_buffer else ""
    streaming_buffer_rows = num_fmt(table.streaming_buffer.estimated_rows) if table.streaming_buffer else ""
    streaming_entry_time = table.streaming_buffer.oldest_entry_time.strftime("%Y-%m-%d %H:%M:%S") if table.streaming_buffer else ""
    return Group(
        text_tuple("Table ID", table.full_table_id),
        text_tuple("Description", table.description),
        text_tuple("Data location", table.location),
        Rule(style=const.darker_style),
        text_tuple("Table size", size),
        text_tuple("Long-term storage size", long_term_size),
        text_tuple("Number of rows", rows),
        Rule(style=const.darker_style),
        text_tuple("Created", created),
        text_tuple("Last modified", modified),
        text_tuple("Table expiry", expiry),
        Rule(style=const.darker_style),
        text_tuple("Partitioned by", partitioned_by),
        text_tuple("Partitioned on field", partitioned_field),
        text_tuple("Partition filter", partition_filter),
        text_tuple("Number of partitions", num_of_partitions),
        Rule(style=const.darker_style),
        text_tuple("Clustered by", table.clustering_fields),
        Rule(style=const.darker_style),
        text_tuple("Streaming buffer rows", streaming_buffer_rows),
        text_tuple("Streaming buffer size", streaming_buffer_size),
        text_tuple("Streaming entry time", streaming_entry_time),
    )
# fmt: on


def text_tuple(name: str, value) -> Text:
    return (
        Text(name, style=const.info_style).append(" = ", style=const.darker_style).append(str(value), style="default")
    )
