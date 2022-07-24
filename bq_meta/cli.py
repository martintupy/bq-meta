import os
from pathlib import Path
from typing import Optional

import click
from rich.console import Console, Group, NewLine
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.text import Text

from bq_meta import const, output
from bq_meta.auth import Auth
from bq_meta.bq_client import BqClient
from bq_meta.config import Config
from bq_meta.service.project_service import ProjectService
from bq_meta.service.meta_service import MetaService


@click.command()
@click.option("-p", "--project-id", help="Project name", default=None)
@click.option("-d", "--dataset-id", help="Dataset name", default=None)
@click.option("-t", "--table-id", help="Table name", default=None)
@click.option("--schema", help="Show schema", is_flag=True)
@click.option("--init", help="Initialize bq_meta environment", is_flag=True)
@click.option("--info", help="Print info of currently logged account", is_flag=True)
@click.option("--set-default-project", help="Set default google project", is_flag=True)
@click.version_option()
def cli(
    project_id: Optional[str],
    dataset_id: Optional[str],
    table_id: Optional[str],
    schema: bool,
    init: bool,
    info: bool,
    set_default_project: bool,
):
    """BiqQuery metadata"""
    ctx = click.get_current_context()
    config = Config(config_path=const.BQ_META_CONFIG)
    console = Console(theme=const.theme, soft_wrap=True)
    auth = Auth(config, console)
    bq_client = BqClient(console, config)
    project_service = ProjectService(console, config, bq_client)
    meta_service = MetaService(console, config, bq_client)
    if init:
        initialize(console, auth, project_service)
        ctx.exit()
    elif info:
        console.print(output.get_config_info(config))
    elif set_default_project:
        project_service.set_project()
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
    elif not config.project:
        panel = Panel(
            title="No project set, run",
            renderable=Text("bq-meta --set-default-project"),
            expand=False,
            padding=(1, 3),
            border_style=const.request_style,
        )
        console.print(panel)
        ctx.exit()
    elif schema:
        meta_service.print_schema()
        ctx.exit()
    else:
        meta_service.print_table_meta(project_id, dataset_id, table_id)


def initialize(console: Console, auth: Auth, project_service: ProjectService):
    bq_meta_home = Prompt.ask(
        Text("", style=const.darker_style).append("Enter bq_meta home path", style=const.request_style),
        default=const.DEFAULT_BQ_META_HOME,
        console=console,
    )
    Path(bq_meta_home).mkdir(parents=True, exist_ok=True)
    console.print(Text("Created", style=const.info_style).append(f": {bq_meta_home}", style=const.darker_style))

    bq_meta_config = f"{bq_meta_home}/config.yaml"
    config = Config(bq_meta_config)
    config.write_default()
    console.print(Text("Created", style=const.info_style).append(f": {bq_meta_config}", style=const.darker_style))

    Prompt.ask(
        Text("", style=const.darker_style).append("Login to google account", style=const.request_style),
        choices=None,
        default="Press enter",
        console=console,
    )
    auth.login()

    Prompt.ask(
        Text("", style=const.darker_style).append("Set google project", style=const.request_style),
        choices=None,
        default="Press enter",
        console=console,
    )
    project_service.set_project()

    if bq_meta_home != const.DEFAULT_BQ_META_HOME:
        group = Group(Text(f"export BQ_META_HOME={bq_meta_home}"))
        console.print(
            NewLine(),
            Panel(
                title="Export following to your environment",
                renderable=group,
                expand=False,
                padding=(1, 3),
                border_style=const.request_style,
            ),
        )
