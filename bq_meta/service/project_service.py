from typing import List

from bq_meta import const
from bq_meta.bq_client import BqClient
from bq_meta.config import Config
from rich.console import Console

from bq_meta.util.rich_utils import progress


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
        projects_ids = ["bigquery-public-data"]  # add bq public datasets explicitly, for testing purposes
        iterator = self.bq_client.client.list_projects()
        for project in progress(self.console, "projects", iterator):
            projects_ids.append(project.project_id)

        with open(self.projects_path, "w") as f:
            f.write("\n".join(projects_ids))
