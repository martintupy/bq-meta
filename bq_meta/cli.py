import os
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from google.cloud.bigquery.table import TableReference

from bq_meta import const, output
from bq_meta.auth import Auth
from google.cloud.bigquery import Client
from bq_meta.config import Config
from bq_meta.initialize import initialize
from bq_meta.service.history_service import HistoryService
from bq_meta.service.project_service import ProjectService
from bq_meta.service.table_service import TableService
from bq_meta.util import table_utils
from bq_meta.util.rich_utils import spinner
from bq_meta.window import Window


def get_client(config: Config):
    def callable():
        return Client(credentials=config.credentials)

    return callable


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
    """BiqQuery metadata"""
    ctx = click.get_current_context()
    config = Config()
    console = Console(theme=const.theme, soft_wrap=True)
    client = spinner(console, get_client(config))
    auth = Auth(config, console)
    project_service = ProjectService(console, config, client)
    table_service = TableService(console, config, client, project_service)
    history_service = HistoryService(console, config, table_service)
    window = Window(console, history_service, table_service)
    table = None
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
        table = table_service.get_table(project_id, dataset_id, table_id)
        if raw:
            console.print_json(table_utils.get_properties(table))
            ctx.exit()
    elif history:
        table = history_service.pick_table()

    window.live_window(table)
