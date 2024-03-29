from typing import List

from loguru import logger
from rich.console import Console

from bq_meta import const
from bq_meta.client import Client
from bq_meta.config import Config
from bq_meta.util.rich_utils import progress


class ProjectService:
    def __init__(self, console: Console, config: Config, client: Client) -> None:
        self.console = console
        self.config = config
        self.client = client
        self.projects_path = const.BQ_META_PROJECTS

    def list_projects(self) -> List[str]:
        logger.trace("Method call")
        projects = open(self.projects_path, "r").read().splitlines()
        return projects

    def fetch_projects(self):
        logger.trace("Method call")
        projects_ids = ["bigquery-public-data"]  # add bq public datasets explicitly, for testing purposes
        iterator = self.client.bq_client.list_projects()
        for project in progress(self.console, "projects", iterator):
            projects_ids.append(project.project_id)
        logger.debug(f"Fetched projects: {projects_ids}")
        with open(self.projects_path, "w") as f:
            f.write("\n".join(projects_ids))
