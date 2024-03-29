from typing import Optional

from bq_meta.client import Client
from bq_meta.config import Config
from bq_meta.service.project_service import ProjectService
from bq_meta.util import bash_util
from bq_meta.util.rich_utils import progress
from google.cloud import bigquery
from rich.console import Console
from rich.live import Live
from loguru import logger


class TableService:
    def __init__(
        self,
        console: Console,
        config: Config,
        client: Client,
        project_service: ProjectService,
    ):
        self.console = console
        self.config = config
        self.client = client
        self.project_service = project_service

    def get_table(
        self,
        project_id: Optional[str] = None,
        dataset_id: Optional[str] = None,
        table_id: Optional[str] = None,
        live: Optional[Live] = None,
    ) -> Optional[bigquery.Table]:
        logger.trace("Method call")
        table = None
        project_id = project_id if project_id else self._pick_project_id(live)
        if project_id:
            dataset_id = dataset_id if dataset_id else self._pick_dataset_id(project_id, live)
        if dataset_id:
            table_id = table_id if table_id else self._pick_table_id(project_id, dataset_id, live)
        if table_id:
            table = self.get_table_str(f"{project_id}.{dataset_id}.{table_id}")
        return table

    def get_table_str(self, table_str: str) -> Optional[bigquery.Table]:
        logger.trace("Method call")
        table = None
        try:
            table = self.client.bq_client.get_table(table_str)
        except Exception:
            logger.warning(f"Table {table_str} not found")
        return table

    def get_fresh_table(self, table: bigquery.Table) -> bigquery.Table:
        logger.trace("Method call")
        return self.get_table_str(f"{table.project}.{table.dataset_id}.{table.table_id}")

    # ======================   Pick   ======================

    def _pick_project_id(self, live: Optional[Live]) -> Optional[str]:
        logger.trace("Method call")
        project_ids = self.project_service.list_projects()
        return bash_util.pick_one(project_ids, live)

    def _pick_dataset_id(self, project_id: str, live: Optional[Live]) -> Optional[str]:
        logger.trace("Method call")
        dataset_ids = []
        iterator = self.client.bq_client.list_datasets(project=project_id)
        for dataset in progress(self.console, "datasets", iterator):
            dataset_ids.append(dataset.dataset_id)
        logger.debug(f"Fetched datasets {dataset_ids}")
        return bash_util.pick_one(dataset_ids, live)

    def _pick_table_id(self, project_id: str, dataset_id: str, live: Optional[Live]) -> Optional[str]:
        logger.trace("Method call")
        table_ids = []
        iterator = self.client.bq_client.list_tables(f"{project_id}.{dataset_id}")
        for table in progress(self.console, "tables", iterator):
            table_ids.append(table.table_id)
        logger.debug(f"Fetched tables {table_ids}")
        return bash_util.pick_one(table_ids, live)
