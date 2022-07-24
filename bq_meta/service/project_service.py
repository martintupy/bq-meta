from typing import List

from bq_meta.bq_client import BqClient, const
from bq_meta.config import Config
from rich.console import Console


class ProjectService:
    def __init__(self, console: Console, config: Config, bq_client: BqClient) -> None:
        self.console = console
        self.config = config
        self.bq_client = bq_client
        self.projects_path = const.BQ_META_PROJECTS

    def list_projects(self) -> List[str]:
        projects = open(self.projects_path, "r").read().splitlines()
        return projects

    def fetch_projects(self):
        projects = self.bq_client.list_projects()
        with open(self.projects_path, "w") as f:
            f.write("\n".join(projects))
