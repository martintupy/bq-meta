import json
from typing import List

import yaml

from bq_meta import const


class Config:
    default = {
        "project": "",
        "client_config": {  # client_config of the google-cloud-sdk
            "installed": {
                "client_id": "32555940559.apps.googleusercontent.com",
                "client_secret": "ZmssLNjJy2998hD4CTg2ejr2",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        "scopes": [
            "https://www.googleapis.com/auth/bigquery",
            "https://www.googleapis.com/auth/userinfo.email",
            "openid",
        ],
        "credentials": None,
        "account": "",
    }

    def __init__(self) -> None:
        self.config_path = const.BQ_META_CONFIG
        self._conf = None

    def write_default(self):
        conf = Config.default
        self._save_conf(conf)

    def _save_conf(self, conf: dict):
        self._conf = conf
        with open(self.config_path, "w") as f:
            yaml.safe_dump(conf, f)

    @property
    def conf(self) -> dict:
        if not self._conf:
            with open(self.config_path, "r") as f:
                self._conf = yaml.safe_load(f)
        return self._conf

    @property
    def client_config(self) -> dict:
        return self.conf["client_config"]

    @property
    def scopes(self) -> List[str]:
        return self.conf["scopes"]

    @property
    def account(self) -> str:
        return self.conf["account"]

    @account.setter
    def account(self, account: str):
        conf = {**self.conf, "account": account}
        self._save_conf(conf)

    @property
    def credentials(self) -> dict:
        return json.loads(self.conf["credentials"])

    @credentials.setter
    def credentials(self, credentials: dict):
        conf = {**self.conf, "credentials": credentials}
        self._save_conf(conf)
