import os
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from google.cloud.bigquery.table import TableReference

from bq_meta import const, output
from bq_meta.auth import Auth
from bq_meta.bq_client import BqClient
from bq_meta.config import Config
from bq_meta.initialize import initialize
from bq_meta.service.history_service import HistoryService
from bq_meta.service.project_service import ProjectService
from bq_meta.service.meta_service import MetaService


@click.command()
@click.argument("full_table_id", required=False)
@click.option("-p", "--project-id", help="Project name", default=None)
@click.option("-d", "--dataset-id", help="Dataset name", default=None)
@click.option("-t", "--table-id", help="Table name", default=None)
@click.option("-h", "--history", help="Show history of past searched tables", is_flag=True)
@click.option("--raw", help="View raw response from the BigQuery in json format", is_flag=True)
@click.option("--init", help="Initialize 'bq-meta' configuration", is_flag=True)
@click.option("--info", help="Print info of currently used account", is_flag=True)
@click.option("--fetch-projects", help="Fetch google projects", is_flag=True)
@click.version_option()
def cli(
    full_table_id: Optional[str],
    project_id: Optional[str],
    dataset_id: Optional[str],
    table_id: Optional[str],
    history: Optional[int],
    raw: bool,
    init: bool,
    info: bool,
    fetch_projects: bool,
):
    """BiqQuery table metadata viewer"""
    ctx = click.get_current_context()
    config = Config()
    console = Console(theme=const.theme, soft_wrap=True)
    auth = Auth(config, console)
    bq_client = BqClient(console, config)
    history_service = HistoryService(console, config)
    project_service = ProjectService(console, config, bq_client)
    meta_service = MetaService(console, config, bq_client, project_service, history_service)
    if init:
        initialize(config, console, auth, project_service)
        ctx.exit()
    elif info:
        console.print(output.get_config_info(config))
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
    elif fetch_projects:
        project_service.fetch_projects()
        ctx.exit()
    elif full_table_id:
        table_ref = TableReference.from_string(full_table_id.replace(":", "."))
        project_id = table_ref.project
        dataset_id = table_ref.dataset_id
        table_id = table_ref.table_id
    elif history:
        from_history = history_service.pick_one()
        table_ref = TableReference.from_string(from_history.replace(":", "."))
        project_id = table_ref.project
        dataset_id = table_ref.dataset_id
        table_id = table_ref.table_id

    meta_service.print_table(project_id, dataset_id, table_id, raw)
