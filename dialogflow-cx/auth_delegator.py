# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module for creating and organizing GCP project credentials."""

import dataclasses
import json
import os

import dialogflow_sample as ds
import google.api_core.exceptions
import google.auth
from google.auth import identity_pool
from google.oauth2 import service_account


def get_credentials(quota_project_id=None):
    """Obtain credentials object from json file and environment configuration."""
    credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    with open(credentials_path, "r", encoding="utf8") as file_handle:
        credentials_data = file_handle.read()
        credentials_dict = json.loads(credentials_data)

    if "client_email" in credentials_dict:
        return service_account.Credentials.from_service_account_file(credentials_path)

    if "audience" in credentials_dict:
        return identity_pool.Credentials.from_info(credentials_dict)

    return google.auth.default(quota_project_id=quota_project_id)[0]


@dataclasses.dataclass(frozen=True)
class AuthDelegator:
    """Class for organizing information related to GCP project credentials configuration."""

    controller: ds.DialogflowSample
    project_id: str
    quota_project_id: None
    location: str = "global"

    @property
    def credentials(self):
        """Access cached credentials."""
        if not self.controller.credentials:
            credentials = get_credentials(quota_project_id=self.quota_project_id)
            self.controller.set_credentials(credentials)
        return self.controller.credentials
