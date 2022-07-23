import re
from dataclasses import dataclass
from datetime import datetime
from typing import List, Mapping, Optional

from dateutil.relativedelta import relativedelta
from google.cloud.bigquery.job.query import QueryJob
from rich.console import Console
from rich.text import Text

from bq_meta import const


@dataclass
class SearchLine:
    created: Text
    query: Text
    project: Text
    account: Text
    job_id: Text

    @staticmethod
    def from_line(line: str):
        parts = line.split(const.FZF_SEPARATOR)
        search_result = None
        if len(parts) == 5:
            search_result = SearchLine(
                created=parts[0],
                query=parts[1],
                project=parts[2].lstrip("project="),
                account=parts[3].lstrip("account="),
                job_id=parts[4].lstrip("id="),
            )
        return search_result

    @staticmethod
    def sort_key(line: str) -> str:
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        escaped = ansi_escape.sub("", line)
        return escaped.split(const.FZF_SEPARATOR)[0]

    def to_line(self, console: Console) -> str:
        sep = Text(const.FZF_SEPARATOR, style=const.darker_style)
        segments = Text.assemble(
            self.created, sep, self.query, sep, self.project, sep, self.account, sep, self.job_id
        ).render(console)
        return console._render_buffer(segments)
