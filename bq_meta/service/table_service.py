from typing import Optional

from bq_meta.bq_client import BqClient
from bq_meta.config import Config
from bq_meta.service.project_service import ProjectService
from bq_meta.util import bash_util
from bq_meta.util.rich_utils import progress
from google.cloud import bigquery
from rich.console import Console
from rich.live import Live


class TableService:
    def __init__(
        self,
        console: Console,
        config: Config,
        bq_client: BqClient,
        project_service: ProjectService,
    ):
        self.console = console
        self.config = config
        self.bq_client = bq_client
        self.project_service = project_service

    def get_table(
        self,
        project_id: Optional[str] = None,
        dataset_id: Optional[str] = None,
        table_id: Optional[str] = None,
        live: Optional[Live] = None,
    ) -> Optional[bigquery.Table]:
        table = None
        project_id = project_id if project_id else self._pick_project_id(live)
        if project_id:
            dataset_id = dataset_id if dataset_id else self._pick_dataset_id(project_id, live)
        if dataset_id:
            table_id = table_id if table_id else self._pick_table_id(project_id, dataset_id, live)
        if table_id:
            table = self.bq_client.client.get_table(f"{project_id}.{dataset_id}.{table_id}")
        return table

    def get_fresh_table(self, table: bigquery.Table) -> bigquery.Table:
        return self.bq_client.client.get_table(f"{table.project}.{table.dataset_id}.{table.table_id}")

    # ======================   Pick   ======================

    def _pick_project_id(self, live: Optional[Live]) -> Optional[str]:
        project_ids = self.project_service.list_projects()
        return bash_util.pick_one(project_ids, live)

    def _pick_dataset_id(self, project_id: str, live: Optional[Live]) -> Optional[str]:
        dataset_ids = []
        iterator = self.bq_client.client.list_datasets(project=project_id)
        for dataset in progress(self.console, "datasets", iterator):
            dataset_ids.append(dataset.dataset_id)
        return bash_util.pick_one(dataset_ids, live)

    def _pick_table_id(self, project_id: str, dataset_id: str, live: Optional[Live]) -> Optional[str]:
        table_ids = []
        iterator = self.bq_client.client.list_tables(f"{project_id}.{dataset_id}")
        for table in progress(self.console, "tables", iterator):
            table_ids.append(table.table_id)
        return bash_util.pick_one(table_ids, live)
