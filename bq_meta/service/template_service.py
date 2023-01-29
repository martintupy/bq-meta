import os
from typing import Optional

import pyperclip
from google.cloud import bigquery
from jinja2 import Template
from rich.live import Live

from bq_meta import const
from bq_meta.util import bash_util


class TemplateService:
    def __init__(self) -> None:
        self.projects_path = const.BQ_META_PROJECTS

    def get_template(self, live: Live) -> Optional[str]:
        templates = next(os.walk(const.BQ_META_TEMPLATES), (None, None, []))[2]
        return bash_util.pick_one(templates, live)

    def template_to_clipboard(self, name: str, table: bigquery.Table) -> None:
        with open(f"{const.BQ_META_TEMPLATES}/{name}") as f:
            rendered = Template(f.read()).render(project=table.project, dataset=table.dataset_id, table=table.table_id)
            pyperclip.copy(rendered)
