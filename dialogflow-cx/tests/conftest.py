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
from basic_webhook_sample import BasicWebhookSample
from set_form_parameter_required_sample import SetFormParameterRequired
from set_session_param_sample import SetSessionParamSample
from utilities import RequestMock
from validate_form_sample import ValidateFormSample
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


@pytest.fixture(name="basic_webhook_sample", scope="function")
def fixture_basic_webhook(session_uuid, project_id, webhook_uri):
    """Test fixture reused for all BasicWebhookSample tests."""
    sample = BasicWebhookSample(
        agent_display_name=f"BasicWebhookSample (test session {session_uuid})",
        project_id=project_id,
        quota_project_id=project_id,
        webhook_uri=webhook_uri,
    )
    sample.setup()
    yield sample
    sample.tear_down()
    del sample


@pytest.fixture(name="validate_form_sample", scope="function")
def fixture_validate_form_sample(session_uuid, project_id, webhook_uri):
    """Test fixture reused for all ValidateFormSample tests."""
    sample = ValidateFormSample(
        agent_display_name=f"ValidateFormSample (test session {session_uuid})",
        project_id=project_id,
        quota_project_id=project_id,
        webhook_uri=webhook_uri,
    )
    sample.setup()
    yield sample
    sample.tear_down()
    del sample


@pytest.fixture(name="set_session_param_sample", scope="function")
def fixture_set_session_param_sample(session_uuid, project_id, webhook_uri):
    """Test fixture reused for all SetSessionParamSample tests."""
    sample = SetSessionParamSample(
        agent_display_name=f"SetSessionParamSample (test session {session_uuid})",
        project_id=project_id,
        quota_project_id=project_id,
        webhook_uri=webhook_uri,
    )
    sample.setup()
    yield sample
    sample.tear_down()
    del sample


@pytest.fixture(name="set_form_parameter_required_sample", scope="function")
def fixture_set_form_parameter_required_sample(session_uuid, project_id, webhook_uri):
    """Test fixture reused for all SetFormParameterRequired tests."""
    sample = SetFormParameterRequired(
        agent_display_name=f"SetFormParameterRequired (test session {session_uuid})",
        project_id=project_id,
        quota_project_id=project_id,
        webhook_uri=webhook_uri,
    )
    sample.setup()
    yield sample
    sample.tear_down()
    del sample
