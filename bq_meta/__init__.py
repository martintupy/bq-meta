import os
from pathlib import Path

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
from bq_meta.service.schema_service import SchemaService


@click.command()
@click.option("--schema", help="Show schema", is_flag=True)
@click.option("--init", help="Initialize bq_meta environment", is_flag=True)
@click.option("--info", help="Print info of currently logged account", is_flag=True)
@click.option("--set-project", help="Set project for queries", is_flag=True)
@click.version_option()
def cli(
    schema: bool,
    init: bool,
    info: bool,
    set_project: bool,
):
    """BiqQuery query."""
    ctx = click.get_current_context()
    config = Config(config_path=const.BQ_META_CONFIG)
    console = Console(theme=const.theme, soft_wrap=True)
    auth = Auth(config, console)
    bq_client = BqClient(console, config)
    project_service = ProjectService(console, config, bq_client)
    schema_service = SchemaService(console, config, bq_client)
    if init:
        initialize(console, auth, project_service)
        ctx.exit()
    elif info:
        console.print(output.get_config_info(config))
    elif set_project:
        project_service.set_project()
    elif not os.path.exists(const.BQ_META_HOME):
        panel = Panel(
            title="Not initialized, run",
            renderable=Text("bq_meta --init"),
            expand=False,
            padding=(1, 3),
            border_style=const.request_style,
        )
        console.print(panel)
        ctx.exit()
    elif not config.project:
        panel = Panel(
            title="No project set, run",
            renderable=Text("bq-meta --set-project"),
            expand=False,
            padding=(1, 3),
            border_style=const.request_style,
        )
        console.print(panel)
        ctx.exit()
    elif schema:
        console.print(schema_service.get_schema())
        ctx.exit()
    else:
        console.print(ctx.get_help())
        ctx.exit()

    # ---------------------- output -------------------------
    


def initialize(console: Console, auth: Auth, project_service: ProjectService):
    bq_meta_home = Prompt.ask(
        Text("", style=const.darker_style).append("Enter bq_meta home path", style=const.request_style),
        default=const.DEFAULT_BQ_META_HOME,
        console=console,
    )
    bq_meta_results = f"{bq_meta_home}/results"
    bq_meta_schemas = f"{bq_meta_home}/schemas"
    bq_meta_infos = f"{bq_meta_home}/infos.json"
    bq_meta_config = f"{bq_meta_home}/config.yaml"
    config = Config(bq_meta_config)

    Path(bq_meta_home).mkdir(parents=True, exist_ok=True)
    console.print(Text("Created", style=const.info_style).append(f": {bq_meta_home}", style=const.darker_style))
    Path(bq_meta_results).mkdir(parents=True, exist_ok=True)
    console.print(Text("Created", style=const.info_style).append(f": {bq_meta_results}", style=const.darker_style))
    Path(bq_meta_schemas).mkdir(parents=True, exist_ok=True)
    console.print(Text("Created", style=const.info_style).append(f": {bq_meta_schemas}", style=const.darker_style))
    Path(bq_meta_infos).touch()
    console.print(Text("Created", style=const.info_style).append(f": {bq_meta_infos}", style=const.darker_style))
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

    if bq_meta_home != const.DEFAULT_bq_meta_HOME:
        group = Group(Text(f"export bq_meta_HOME={bq_meta_home}"))
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
