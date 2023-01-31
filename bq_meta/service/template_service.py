import os
from typing import Optional

from google.cloud import bigquery
from jinja2 import Template
from rich.live import Live

from bq_meta import const
from bq_meta.util import bash_util


class TemplateService:
    def __init__(self) -> None:
        self.projects_path = const.BQ_META_PROJECTS

    def list_templates(self):
        return next(os.walk(const.BQ_META_TEMPLATES), (None, None, []))[2]

    def get_template(self, template: str, table: bigquery.Table) -> Optional[str]:
        rendered = None
        if template:
            with open(f"{const.BQ_META_TEMPLATES}/{template}") as f:
                rendered = Template(f.read()).render(
                    project=table.project,
                    dataset=table.dataset_id,
                    table=table.table_id,
                )
        return rendered
