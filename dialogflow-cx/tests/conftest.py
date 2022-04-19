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
import os
import uuid
from typing import Generator

import pytest
from utilities import RequestMock
from webhook.main import get_webhook_uri


@pytest.fixture(scope="function")
def mocked_request() -> Generator[RequestMock, None, None]:
    """Test fixture providing a mocked flask.Request interface."""
    request = RequestMock()
    yield request
    del request


@pytest.fixture(name="session_uuid", scope="session")
def fixture_session_uuid():
    """Test fixture providing a unique ID for the test session."""
    return uuid.uuid4()


@pytest.fixture(name="project_id", scope="session")
def fixture_project_id():
    """Test fixture providing a project ID used for testing."""
    return os.environ["PROJECT_ID"]


@pytest.fixture(name="build_uuid", scope="session")
def fixture_build_uuid():
    """Test fixture providing a unique ID for the test build."""
    return os.environ["BUILD_UUID"]


@pytest.fixture(name="webhook_uri", scope="session")
def fixture_webhook_uri(project_id, build_uuid):
    """Test fixture providings the URI for the fixture webhook."""
    return get_webhook_uri(project_id, build_uuid)
