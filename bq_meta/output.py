from typing import List, Optional

from google.cloud import bigquery
from packaging import version
from rich.align import Align
from rich.box import SIMPLE
from rich.columns import Columns
from rich.console import Group, NewLine, RenderableType
from rich.layout import Layout
from rich.panel import Panel
from rich.rule import Rule
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from bq_meta import const
from bq_meta.config import Config
from bq_meta.util import table_utils
from bq_meta.util.num_utils import bytes_fmt, num_fmt
from bq_meta.window import Hint

title = """
██▄ █ ▄▀  ▄▀▄ █ █ ██▀ █▀▄ ▀▄▀   █▄ ▄█ ██▀ ▀█▀ ▄▀▄ █▀▄ ▄▀▄ ▀█▀ ▄▀▄
█▄█ █ ▀▄█ ▀▄█ ▀▄█ █▄▄ █▀▄  █    █ ▀ █ █▄▄  █  █▀█ █▄▀ █▀█  █  █▀█
"""


def header_layout(config: Config) -> Layout:
    header_title = Align(title, align="center", style=const.info_style)
    header = Layout(name="header", size=4)
    left = version_layout(config)
    mid = Layout(header_title)
    right = Layout(NewLine(), size=20)
    header.split_row(left, mid, right)
    return header


def version_layout(config: Config) -> Layout:
    if config.current_version and config.available_version:
        current = version.parse(config.current_version)
        available = version.parse(config.available_version)
        if current < available:
            version_text = Text(f"{current} ► {available}", style=const.darker_style)
        else:
            version_text = Text(f"{current}", style=const.darker_style)
    else:
        version_text = Text(" ", style=const.darker_style)
    return Layout(version_text, name="version", size=20)


def list_layout(values: List[str], selected: Optional[str]) -> Layout:
    show = values and selected
    panel = Panel(NewLine())
    if show:
        separator = Rule(style=const.darker_style)
        values_list = []
        for value in values:
            if value == selected:
                text = Text(f"● {value}", style=const.info_style)
            else:
                text = Text(f"  {value}", style="default")
            values_list.extend([text, separator])
        panel = Panel(Group(*values_list), box=const.box_right_rounded, style=const.darker_style)
    return Layout(panel, size=30, visible=show)


def content_layout(renderable: Optional[RenderableType]) -> Layout:
    if renderable:
        content = Panel(renderable, border_style=const.darker_style)
    else:
        content = Panel(NewLine(), border_style=const.darker_style)
    return Layout(content, name="content")


def hints_layout(hints: List[Hint], bottom_hints: List[Hint]) -> Layout:
    hints_layout = Layout(name="hints")
    separator = Rule(style=const.darker_style)
    hints_list = []
    for hint in hints:
        text = Text(f"{hint.name} ({hint.key})", style="default")
        hints_list.extend([text, separator])
    top = Layout(Group(*hints_list))
    bottom_hints_list = []
    for bottom_hint in bottom_hints:
        text = Text(f"{bottom_hint.name} ({bottom_hint.key})", style="default")
        bottom_hints_list.extend([separator, text])
    bottom = Layout(Align(Group(*bottom_hints_list, fit=False), vertical="bottom"))
    hints_layout.split_column(top, bottom)
    return Layout(Panel(hints_layout, box=const.box_left_rounded, style=const.darker_style), size=30)


def get_config_info(config: Config) -> Group:
    return Group(text_tuple("Account", config.account))


def get_schema_output(table: bigquery.Table) -> Group:
    schema = table.schema
    tree = Tree(Text(table.full_table_id, const.key_style))
    table = Table(box=SIMPLE, show_header=False)
    table_utils.scheme_tree(schema, tree)
    table_utils.scheme_table(schema, table)
    return Group(Rule("Schema", style=const.darker_style), Columns([tree, table]))


def get_snippet_output(snippet: str) -> Group:
    syntax = Syntax(snippet, lexer="SqlLexer", line_numbers=True, theme="ansi_dark")
    return Group(Rule("Snippet", style=const.darker_style), syntax)


# fmt: off
def get_table_output(table: bigquery.Table) -> Group:
    total_logical_bytes = bytes_fmt(int(table._properties.get("numTotalLogicalBytes", 0)))
    active_logical_bytes = bytes_fmt(int(table._properties.get("numActiveLogicalBytes", 0)))
    long_term_logical_bytes = bytes_fmt(int(table._properties.get("numLongTermLogicalBytes", 0)))
    total_physical_bytes = bytes_fmt(int(table._properties.get("numTotalPhysicalBytes", 0)))
    active_physical_bytes = bytes_fmt(int(table._properties.get("numActivePhysicalBytes", 0)))
    long_term_physical_bytes = bytes_fmt(int(table._properties.get("numLongTermPhysicalBytes", 0)))
    time_travel_physical_bytes = bytes_fmt(int(table._properties.get("numTimeTravelPhysicalBytes", 0)))
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
        Rule("Table info", style=const.darker_style),
        table_tuple({
            "Table ID": table.full_table_id,
            "Friendly name": table.friendly_name,
            "Created": created,
            "Last modified": modified,
            "Table expiry": expiry,
            "Data location": table.location,
            "Data location": table.location,
            "Description": table.description,
        }),
        Rule(style=const.darker_style),
        table_tuple({
            "Table type": table.table_type,
            "Partitioned by": partitioned_by,
            "Partitioned on field": partitioned_field,
            "Partition expiry": table.partition_expiration,
            "Partition filter": partition_filter,
            "Clustered by": table.clustering_fields,
        }),
        Rule("Storage info", style=const.darker_style),
        table_tuple({
            "Number of row": rows, 
            "Number of partitions": num_of_partitions, 
            "Total logical bytes": total_logical_bytes, 
            "Active logical bytes": active_logical_bytes, 
            "Long-term logical bytes": long_term_logical_bytes, 
            "Total physical bytes": total_physical_bytes, 
            "Active physical bytes": active_physical_bytes, 
            "Long-term physical bytes": long_term_physical_bytes, 
            "Time travel physical bytes": time_travel_physical_bytes, 
        }),
        Rule("Streaming buffer statistics", style=const.darker_style),
        table_tuple({
            "Estimated size": streaming_buffer_size,
            "Estimated rows": streaming_buffer_rows,
            "Earliest entry time": streaming_entry_time,
        }),
        Rule(style=const.darker_style),
    )
# fmt: on


def table_tuple(tuples: dict) -> Text:
    table = Table(
        box=const.equal_box,
        show_header=False,
        show_edge=False,
        pad_edge=False,
        border_style=const.darker_style,
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
