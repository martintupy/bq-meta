from typing import List

from loguru import logger
from rich.console import Console

from bq_meta.client import Client
from bq_meta.config import Config
from bq_meta.util.rich_utils import progress
from google.cloud.bigquery import Table

from google.cloud.asset_v1 import AnalyzeIamPolicyRequest, IamPolicyAnalysisQuery


class IamService:
    def __init__(self, console: Console, config: Config, client: Client) -> None:
        self.console = console
        self.config = config
        self.client = client
        self.table = None
        self.role_members = {}

    def fetch_all_roles_members(self, table: Table, roles: List[str]) -> bool:
        logger.trace("Method call")
        try:
            self.table = table
            request = AnalyzeIamPolicyRequest()
            analysis_query = IamPolicyAnalysisQuery()
            analysis_query.scope = f"projects/{table.project}"
            analysis_query.access_selector.roles = roles
            analysis_query.resource_selector.full_resource_name = (
                f"//bigquery.googleapis.com/projects/{table.project}/datasets/{table.dataset_id}/tables/{table.table_id}"
            )
            request.analysis_query = analysis_query
            logger.debug(request)
            response = self.client.asset_client.analyze_iam_policy(request=request)
            self.role_members = {}
            for result in response.main_analysis.analysis_results:
                self.role_members[result.iam_binding.role] = result.iam_binding.members
            logger.debug(f"Fetched all roles members: {self.role_members}")
            return True
        except Exception as e:
            logger.warning(e)
            return False
            

    def get_role_members(self, table: Table, role: str) -> List[str]:
        logger.trace("Method call")
        members = []
        if self.table.full_table_id == table.full_table_id:
            members = self.role_members[role]
        return members
