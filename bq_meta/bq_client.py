from google.cloud.bigquery import Client
from google.oauth2.credentials import Credentials
from rich.console import Console
from rich.text import Text

from bq_meta import const
from bq_meta.config import Config


class BqClient:
    def __init__(self, console: Console, config: Config):
        self._client = None
        self.console = console
        self.config = config

    @property
    def client(self) -> Client:
        if not self._client:
            with self.console.status(Text("Connecting to the API", style=const.darker_style), spinner="point"):
                self._client = Client(
                    project="",  # leaving project as None would result in error
                    credentials=Credentials.from_authorized_user_info(self.config.credentials),
                )
        return self._client
