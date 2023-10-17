import os
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from google.cloud.bigquery.table import TableReference

from bq_meta import const, output
from bq_meta.client import Client
from bq_meta.config import Config
from bq_meta.initialize import initialize
from bq_meta.service.history_service import HistoryService
from bq_meta.service.iam_service import IamService
from bq_meta.service.project_service import ProjectService
from bq_meta.service.table_service import TableService
from bq_meta.service.snippet_service import SnippetService
from bq_meta.service.version_service import VersionService
from bq_meta.util import table_utils
from bq_meta.window import Window
from loguru import logger
import os


@click.command()
@click.argument("full_table_id", required=False)
@click.option("--raw", help="View raw response from the BigQuery for specific 'FULL_TABLE_ID'", is_flag=True)
@click.option("--init", help="Initialize 'bq-meta' configuration", is_flag=True)
@click.option("--info", help="Print info of currently used account", is_flag=True)
@click.option("--fetch-projects", help="Fetch available google projects", is_flag=True)
@click.option("--debug", help="Log debug messages into BQ_META_HOME/debug.log", is_flag=True)
@click.option("--trace", help="Log tace messages into BQ_META_HOME/trace.log", is_flag=True)
@click.version_option()
def cli(
    full_table_id: Optional[str],
    raw: bool,
    init: bool,
    info: bool,
    fetch_projects: bool,
    debug: bool,
    trace: bool,
):
    """BiqQuery metadata"""

    ctx = click.get_current_context()
    console = Console(theme=const.theme, soft_wrap=True, force_interactive=True)
    config = Config()
    client = Client(console, config)
    project_service = ProjectService(console, config, client)
    table_service = TableService(console, config, client, project_service)
    snippet_service = SnippetService()
    history_service = HistoryService(console, config, table_service)
    iam_service = IamService(console, config, client)
    window = Window(console, config, history_service, table_service, snippet_service, iam_service)
    table = None

    logger.remove(0)  # disable stdout handler
    logger.level("DEBUG", color="<fg #008720>")
    logger.level("TRACE", color="<fg #6CEC16>")
    if debug:
        logger.add(const.BQ_META_DEBUG, colorize=True, level="DEBUG", rotation="1 MB", format=const.logger_format)
    if trace:
        logger.add(const.BQ_META_TRACE, colorize=True, level="TRACE", rotation="1 MB", format=const.logger_format)

    if os.path.exists(const.BQ_META_HOME):
        version_service = VersionService()
        version_service.update_config(config)

    logger.debug(f"Loaded config: {config.conf}")

    if init:
        initialize(config, console, project_service)
        ctx.exit()
    elif not os.path.exists(const.BQ_META_HOME):
        panel = Panel(
            title="Not initialized, run",
            renderable=Text("bq-meta --init"),
            expand=False,
            padding=(1, 3),
            border_style=const.request_style,
        )
        console.print(panel)
        ctx.exit()
    elif info:
        console.print(output.get_config_info(config))
        ctx.exit()
    elif fetch_projects:
        project_service.fetch_projects()
        ctx.exit()
    elif full_table_id:
        table_ref = TableReference.from_string(full_table_id.replace(":", "."))
        project_id = table_ref.project
        dataset_id = table_ref.dataset_id
        table_id = table_ref.table_id
        table = table_service.get_table(project_id, dataset_id, table_id)
        if raw:
            console.print_json(table_utils.get_properties(table))
            ctx.exit()

    window.live_window(table)
