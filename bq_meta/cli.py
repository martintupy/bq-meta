import os
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from google.cloud.bigquery.table import TableReference

from bq_meta import const, output
from bq_meta.bq_client import BqClient
from bq_meta.config import Config
from bq_meta.initialize import initialize
from bq_meta.service.history_service import HistoryService
from bq_meta.service.project_service import ProjectService
from bq_meta.service.table_service import TableService
from bq_meta.service.version_service import VersionService
from bq_meta.util import table_utils
from bq_meta.window import Window


@click.command()
@click.argument("full_table_id", required=False)
@click.option("--raw", help="View raw response from the BigQuery for specific 'FULL_TABLE_ID'", is_flag=True)
@click.option("--init", help="Initialize 'bq-meta' configuration", is_flag=True)
@click.option("--info", help="Print info of currently used account", is_flag=True)
@click.option("--fetch-projects", help="Fetch available google projects", is_flag=True)
@click.version_option()
def cli(
    full_table_id: Optional[str],
    raw: bool,
    init: bool,
    info: bool,
    fetch_projects: bool,
):
    """BiqQuery metadata"""

    ctx = click.get_current_context()
    console = Console(theme=const.theme, soft_wrap=True, force_interactive=True)
    config = Config()
    bq_client = BqClient(console, config)
    project_service = ProjectService(console, config, bq_client)
    table_service = TableService(console, config, bq_client, project_service)
    history_service = HistoryService(console, config, table_service)
    window = Window(console, config, history_service, table_service)
    table = None
    
    if os.path.exists(const.BQ_META_HOME):
        version_service = VersionService()
        version_service.update_config(config)

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
