from bq_meta.config import Config
import requests
from importlib.metadata import version


class VersionService:
    def __init__(self):
        ...

    def update_config(self, config: Config):
        available_version = VersionService._get_available_version()
        current_version = VersionService._get_current_version()
        config.available_version = available_version
        config.current_version = current_version

    def _get_available_version() -> str:
        package = "bq-meta"
        url = f"https://pypi.org/pypi/{package}/json"
        response: dict = requests.request("GET", url).json()
        version = response.get("info", None).get("version", None)
        return version

    def _get_current_version() -> str:
        try:
            ver = version("bq-meta")
        except:
            ver = None
        return ver

