import os
from typing import Optional

from google.cloud import bigquery
from jinja2 import Template
from loguru import logger

from bq_meta import const


class SnippetService:
    def __init__(self) -> None:
        self.projects_path = const.BQ_META_PROJECTS

    def list_snippets(self):
        logger.trace("Method call")
        return next(os.walk(const.BQ_META_SNIPPETS), (None, None, []))[2]

    def get_snippet(self, snippet: str, table: bigquery.Table) -> Optional[str]:
        logger.trace("Method call")
        rendered = None
        if snippet:
            with open(f"{const.BQ_META_SNIPPETS}/{snippet}") as f:
                rendered = Template(f.read()).render(
                    project=table.project,
                    dataset=table.dataset_id,
                    table=table.table_id,
                )
        logger.debug(f"Rendered snippet: {const.BQ_META_SNIPPETS}/{snippet}")
        return rendered
