from pathlib import Path

from rich.console import Console, Group, NewLine
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from bq_meta import const
from bq_meta.auth import Auth
from bq_meta.config import Config
from bq_meta.service.project_service import ProjectService


def initialize(config: Config, console: Console, project_service: ProjectService):
    bq_meta_home = Prompt.ask(
        Text("", style=const.darker_style).append("Enter bq_meta home path", style=const.request_style),
        default=const.DEFAULT_BQ_META_HOME,
        console=console,
    )

    Path(bq_meta_home).mkdir(parents=True, exist_ok=True)
    _print_created(console, bq_meta_home)
    Path(const.BQ_META_CONFIG).touch()
    config.write_default()
    _print_created(console, const.BQ_META_CONFIG)
    Path(const.BQ_META_PROJECTS).touch()
    _print_created(console, const.BQ_META_PROJECTS)
    Path(const.BQ_META_HISTORY).touch()
    _print_created(console, const.BQ_META_HISTORY)

    Prompt.ask(
        Text("", style=const.darker_style).append("Login to google account", style=const.request_style),
        choices=None,
        default="Press enter",
        console=console,
    )
    auth = Auth(config, console)
    auth.login()

    project_service.fetch_projects()

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


def _print_created(console: Console, path: str):
    console.print(Text("Created", style=const.info_style).append(f": {path}", style=const.darker_style))
