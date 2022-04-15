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

from webhook.main import webhook_fcn, build_request_dict_basic, extract_text


@pytest.mark.hermetic
def test_basic_webhook(mocked_request):

    # Arrange:
    mock_tag = "basic_webhook"
    mock_text = "MOCK TEXT"
    mocked_request.payload = build_request_dict_basic(mock_tag, mock_text)

    # Act:
    response_json = webhook_fcn(mocked_request)

    # Assert:
    assert (
        extract_text(response_json)
        == f"Webhook received: {mock_text} (Tag: {mock_tag})"
    )


@pytest.mark.hermetic
@pytest.mark.parametrize(
    "test_input,expected",
    [
        (1, "Valid age"),
        (-1, "Age -1 not valid (must be positive)"),
    ],
)
def test_validate_form(mocked_request, test_input, expected):

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
