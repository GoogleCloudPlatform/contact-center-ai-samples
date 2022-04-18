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

from validate_form_sample import ValidateFormSample
from basic_webhook_sample import BasicWebhookSample


@pytest.fixture(scope="function")
def mocked_request() -> Generator[RequestMock, None, None]:
    request = RequestMock()
    yield request
    del request


@pytest.fixture(scope="session")
def session_uuid():
    return uuid.uuid4()


@pytest.fixture(scope="session")
def project_id():
    return os.environ["PROJECT_ID"]


@pytest.fixture(scope="session")
def build_uuid():
    return os.environ["BUILD_UUID"]


@pytest.fixture(scope="session")
def webhook_uri(project_id, build_uuid):
    return get_webhook_uri(project_id, build_uuid)


@pytest.fixture(scope="session")
def validate_form_webhook_sample(session_uuid, project_id, webhook_uri):
    """Test fixture reused for all ValidateFormSample tests."""
    sample = ValidateFormSample(
        agent_display_name=f"ValidateFormSample (test session {session_uuid})",
        project_id=project_id,
        webhook_uri=webhook_uri,
    )
    sample.initialize()
    yield sample
    sample.tear_down()
    del sample


@pytest.fixture(scope="session")
def basic_webhook_sample(session_uuid, project_id, webhook_uri):
    """Test fixture reused for all BasicWebhookSample tests."""
    sample = BasicWebhookSample(
        agent_display_name=f"BasicWebhookSample (test session {session_uuid})",
        project_id=project_id,
        webhook_uri=webhook_uri,
    )
    sample.initialize()
    yield sample
    sample.tear_down()
    del sample