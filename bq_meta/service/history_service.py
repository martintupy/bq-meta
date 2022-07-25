from typing import List

from bq_meta.bq_client import const
from bq_meta.config import Config
from rich.console import Console
from google.cloud.bigquery.table import Table

from bq_meta.util import bash_util


class HistoryService:
    def __init__(self, console: Console, config: Config) -> None:
        self.console = console
        self.config = config
        self.history_path = const.BQ_META_HISTORY

    def list_history(self) -> List[str]:
        projects = open(self.history_path, "r").read().splitlines()
        return projects

    def save_one(self, table: Table):
        history = self.list_history()
        try:
            history.remove(table.full_table_id)
        except ValueError:
            pass
        history.append(table.full_table_id)
        with open(self.history_path, "w") as f:
            f.write("\n".join(history))

    def pick_one(self) -> str:
        history = self.list_history()
        return bash_util.pick_one(history, self.console)
