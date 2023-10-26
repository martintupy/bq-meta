from typing import List, Optional

from bq_meta import const
from bq_meta.config import Config
from bq_meta.service.table_service import TableService
from bq_meta.util import bash_util
from google.cloud.bigquery.table import Table, TableReference
from rich.console import Console
from rich.live import Live
from loguru import logger


class HistoryService:
    def __init__(self, console: Console, config: Config, table_service: TableService) -> None:
        self.console = console
        self.config = config
        self.table_service = table_service
        self.history_path = const.BQ_META_HISTORY

    def list_tables(self) -> List[str]:
        logger.trace("Method call")
        projects = open(self.history_path, "r").read().splitlines()
        return projects

    def purge_tables(self):
        logger.trace("Method call")
        history = self.list_tables()
        new_history = []
        for table in history:
            if self.table_service.get_table_str(table.replace(":", ".")):
                new_history.append(table)
        with open(self.history_path, "w") as f:
            f.write("\n".join(new_history))
        logger.debug("Purged history")

    def save_table(self, table: Table):
        logger.trace("Method call")
        history = self.list_tables()
        try:
            history.remove(table.full_table_id)
        except ValueError:
            pass
        history.append(table.full_table_id)
        with open(self.history_path, "w") as f:
            f.write("\n".join(history))
        logger.debug(f"Saved table: {table}")

    def remove_table(self, table_ref: str):
        logger.trace("Method call")
        history = self.list_tables()
        try:
            history.remove(table_ref)
        except ValueError:
            pass
        with open(self.history_path, "w") as f:
            f.write("\n".join(history))
        logger.debug(f"Removed table: {table_ref}")

    def pick_table(self, live: Optional[Live]) -> Optional[Table]:
        logger.trace("Method call")
        history = self.list_tables()
        from_history = bash_util.pick_one(history, live)
        table = None
        if from_history:
            table_ref = TableReference.from_string(from_history.replace(":", "."))
            project_id = table_ref.project
            dataset_id = table_ref.dataset_id
            table_id = table_ref.table_id
            table = self.table_service.get_table(project_id, dataset_id, table_id, live)
            if not table:
                self.remove_table(from_history)
        logger.debug(f"Picked table: {table}")
        return table
