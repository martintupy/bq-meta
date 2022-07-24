from bq_meta.bq_client import BqClient, const
from bq_meta.config import Config
from bq_meta.util import bash_util
from rich.console import Console
from rich.text import Text


class ProjectService:
    def __init__(self, console: Console, config: Config, bq_client: BqClient) -> None:
        self.console = console
        self.config = config
        self.bq_client = bq_client

    def set_project(self):
        projects = self.bq_client.list_projects()
        project = next(iter(bash_util.fzf(projects)), None)
        if project:
            self.config.project = project
            self.console.print(
                Text("Project updated", style=const.info_style).append(f": {project}", style=const.darker_style)
            )
