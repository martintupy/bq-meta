from google.cloud.bigquery import Client as BigQueryClient
from google.oauth2.credentials import Credentials
from rich.console import Console

from bq_meta.config import Config


class Client:
    def __init__(self, console: Console, config: Config):
        self._bq_client = None
        self._connection_client = None
        self._location_client = None
        self.console = console
        self.config = config

    @property
    def bq_client(self) -> BigQueryClient:
        if not self._bq_client:
            self._bq_client = BigQueryClient(
                project="",  # leaving project as None would result in error
                credentials=Credentials.from_authorized_user_info(self.config.credentials),
            )
        return self._bq_client