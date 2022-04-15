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

"""Module providing fixtures for the entire test directory."""
from typing import Generator

import pytest

# from webhook_sample import DialogflowController
from google.auth import credentials as ga_credentials
from utilities import RequestMock


@pytest.fixture(scope="function")
def mocked_request() -> Generator[RequestMock, None, None]:
    request = RequestMock()
    yield request
    del request


@pytest.fixture(scope="session")
def project_id() -> str:
    return "MOCK_PROJECT_ID_FIXTURE"


@pytest.fixture(scope="session")
def mock_project_id_env() -> str:
    return "MOCK_PROJECT_ID_ENV"


@pytest.fixture(scope="function")
def mock_credentials() -> Generator[ga_credentials.Credentials, None, None]:
    credentials = ga_credentials.AnonymousCredentials()
    yield credentials
    del credentials


# @pytest.fixture()
# def mock_settings_env_vars(mock_project_id_env):
#     with mock.patch.dict(os.environ, {PROJECT: mock_project_id_env}):
#         yield


# @pytest.fixture(scope='function')
# def controller(project_id) -> DialogflowController:
#   dfc = DialogflowController(project_id=project_id)
#   yield dfc
#   del dfc
