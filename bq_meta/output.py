from rich.console import Group
from rich.text import Text

from bq_meta import const
from bq_meta.config import Config


def get_gcloud_info(json: dict) -> Group:
    project = json.get("config", {}).get("project")
    account = json.get("config", {}).get("account")
    return Group(
        Text("Project", style=const.info_style).append(f" = {project}", style="default"),
        Text("Account", style=const.info_style).append(f" = {account}", style="default"),
    )


def get_config_info(config: Config) -> Group:
    return Group(
        Text("Project", style=const.info_style).append(f" = {config.project}", style="default"),
        Text("Account", style=const.info_style).append(f" = {config.account}", style="default"),
    )
