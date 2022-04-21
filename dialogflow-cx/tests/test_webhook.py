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

"""Tests for webhook module."""

import pytest
from webhook.main import (
    build_request_dict_basic,
    extract_session_parameters,
    extract_text,
    webhook_fcn,
)


@pytest.mark.hermetic
def test_basic_webhook(mocked_request):
    """Locally tests the entry fulfillment webhook function."""

    # Arrange:
    mock_tag = "basic_webhook"
    mock_text = "MOCK TEXT"
    mocked_request.payload = build_request_dict_basic(mock_tag, mock_text)

    # Act:
    response_json = webhook_fcn(mocked_request)

    # Assert:
    expected = f"Webhook received: {mock_text} (Tag: {mock_tag})"
    assert extract_text(response_json) == expected


@pytest.mark.hermetic
@pytest.mark.parametrize(
    "test_input,expected",
    [
        (1, "Valid age"),
        (-1, "Age -1 not valid (must be positive)"),
    ],
)
def test_validate_form(mocked_request, test_input, expected):
    """Locally tests the form validation webhook function."""

    # Arrange:
    request_mapping = {}
    request_mapping["fulfillmentInfo"] = {}
    request_mapping["fulfillmentInfo"]["tag"] = "validate_form"
    request_mapping["pageInfo"] = {}
    request_mapping["pageInfo"]["formInfo"] = {}
    request_mapping["pageInfo"]["formInfo"]["parameterInfo"] = [
        {"displayName": "age", "value": test_input}
    ]
    mocked_request.payload = request_mapping

    # Act:
    response_json = webhook_fcn(mocked_request)

    # Assert:
    assert extract_text(response_json) == expected


@pytest.mark.hermetic
def test_set_session_param(mocked_request):
    """Locally tests the set session parameter webhook function."""

    # Arrange:
    mock_key = "MOCK_KEY"
    mock_val = "MOCK_VAL"
    request_mapping = {}
    request_mapping["fulfillmentInfo"] = {}
    request_mapping["fulfillmentInfo"]["tag"] = "set_session_param"
    request_mapping["sessionInfo"] = {}
    request_mapping["sessionInfo"]["parameters"] = {
        "key": mock_key,
        "val": mock_val,
    }
    mocked_request.payload = request_mapping

    # Act:
    response_json = webhook_fcn(mocked_request)

    # Assert:
    assert extract_text(response_json) == "Session parameter set"
    assert extract_session_parameters(response_json)[mock_key] == mock_val
