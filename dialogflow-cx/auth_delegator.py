import json
import os

import dialogflow_sample as ds
import google.api_core.exceptions
import google.auth
from google.auth import identity_pool
from google.oauth2 import service_account


def get_credentials(quota_project_id=None):

    credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    with open(credentials_path, "r", encoding="utf8") as f:
        credentials_data = f.read()
        credentials_dict = json.loads(credentials_data)

    if "client_email" in credentials_dict:
        return service_account.Credentials.from_service_account_file(credentials_path)

    if "audience" in credentials_dict:
        return identity_pool.Credentials.from_info(credentials_dict)

    return google.auth.default(quota_project_id=quota_project_id)[0]


class AuthDelegator:

    _DEFAULT_LOCATION = "global"

    def __init__(
        self,
        controller: ds.DialogflowSample,
        project_id=None,
        quota_project_id=None,
        credentials=None,
        **kwargs,
    ):
        self.location = kwargs.get("location", self._DEFAULT_LOCATION)
        self.project_id = project_id
        self.controller = controller
        if not quota_project_id:
            quota_project_id = project_id
        self.quota_project_id = quota_project_id
        self.credentials = (
            credentials
            if credentials
            else get_credentials(quota_project_id=quota_project_id)
        )
