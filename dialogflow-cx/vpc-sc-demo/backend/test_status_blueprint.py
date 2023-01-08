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

"""Module for testing status_blueprint.py."""

import json
from urllib.parse import urlparse

import get_token
import pytest
import requests
import status_utilities as su
from conftest import MOCK_DOMAIN, MockReturnObject
from mock import patch
from status_blueprint import status as blueprint


def assert_response(
    return_value, status_code, endpoint, response=None, netloc=MOCK_DOMAIN
):
    """Assert function for testing responses"""
    parsed_url = urlparse(return_value.request.url)
    assert return_value.headers["Content-Type"] == "text/html; charset=utf-8"
    assert parsed_url.scheme == "https"
    assert parsed_url.netloc == netloc
    assert parsed_url.path == endpoint
    assert return_value.status_code == status_code
    if response is not None:
        for curr_response in return_value.response:
            assert curr_response.decode() == response


@pytest.mark.hermetic
@pytest.mark.parametrize(
    "app, endpoint",
    [
        (blueprint, "/webhook_ingress_internal_only_status"),
        (blueprint, "/webhook_access_allow_unauthenticated_status"),
        (blueprint, "/restricted_services_status_cloudfunctions"),
        (blueprint, "/restricted_services_status_dialogflow"),
        (blueprint, "/service_directory_webhook_fulfillment_status"),
    ],
    indirect=["app"],
)
def test_restricted_services_status_bad_token(app, endpoint):
    """Test restricted services status, bad token."""
    with patch.object(
        get_token, "get_token", return_value={"response": "MOCK_RESPONSE"}
    ):
        with app.test_client() as curr_client:
            return_value = curr_client.get(endpoint, base_url=f"https://{MOCK_DOMAIN}")
    assert_response(return_value, 200, endpoint, "MOCK_RESPONSE")


@pytest.mark.hermetic
@pytest.mark.parametrize(
    "app, endpoint",
    [
        (blueprint, "/webhook_ingress_internal_only_status"),
        (blueprint, "/webhook_access_allow_unauthenticated_status"),
        (blueprint, "/restricted_services_status_cloudfunctions"),
        (blueprint, "/restricted_services_status_dialogflow"),
        (blueprint, "/service_directory_webhook_fulfillment_status"),
    ],
    indirect=["app"],
)
def test_restricted_services_status_no_project(app, endpoint):
    """Test restricted services status, no project."""
    with patch.object(
        get_token, "get_token", return_value={"access_token": "MOCK_ACCESS_TOKEN"}
    ):
        with app.test_client() as curr_client:
            return_value = curr_client.get(endpoint, base_url=f"https://{MOCK_DOMAIN}")
    assert_response(
        return_value,
        200,
        endpoint,
        json.dumps({"status": "BLOCKED", "reason": "NO_PROJECT_ID"}),
    )


def get_result(
    app,
    endpoint,
    mock_project_id="MOCK_PROJECT_ID",
    mock_region=None,
    mock_webhook_name=None,
):
    """Helper function to get result from a test client."""
    query_string = {}
    if mock_project_id:
        query_string["project_id"] = mock_project_id
    if mock_region:
        query_string["region"] = mock_region
    if mock_webhook_name:
        query_string["webhook_name"] = mock_webhook_name
    with app.test_client() as curr_client:
        return curr_client.get(
            endpoint,
            base_url=f"https://{MOCK_DOMAIN}",
            query_string=query_string,
        )


@pytest.mark.hermetic
@pytest.mark.parametrize(
    "app, endpoint",
    [
        (blueprint, "/restricted_services_status_cloudfunctions"),
        (blueprint, "/restricted_services_status_dialogflow"),
    ],
    indirect=["app"],
)
def test_restricted_services_status_no_policy(app, endpoint):
    """Test restricted services status, no policy."""
    with patch.object(
        get_token, "get_token", return_value={"access_token": "MOCK_ACCESS_TOKEN"}
    ):
        with patch.object(
            su, "get_access_policy_name", return_value={"response": "MOCK_RESPONSE"}
        ):
            return_value = get_result(app, endpoint)
    assert_response(return_value, 200, endpoint, "MOCK_RESPONSE")


@pytest.mark.hermetic
@pytest.mark.parametrize(
    "app, endpoint",
    [
        (blueprint, "/restricted_services_status_cloudfunctions"),
        (blueprint, "/restricted_services_status_dialogflow"),
    ],
    indirect=["app"],
)
def test_restricted_services_status_restricted(app, endpoint):
    """Test restricted services status, restricted."""
    with patch.object(
        get_token, "get_token", return_value={"access_token": "MOCK_ACCESS_TOKEN"}
    ):
        with patch.object(
            su,
            "get_access_policy_name",
            return_value={"access_policy_name": "MOCK_ACCESS_POLICY_NAME"},
        ):
            with patch.object(
                su,
                "get_restricted_services_status",
                return_value={"response": "MOCK_RESPONSE"},
            ):
                return_value = get_result(app, endpoint)
        assert_response(return_value, 200, endpoint, "MOCK_RESPONSE")


@pytest.mark.hermetic
@pytest.mark.parametrize(
    "app, endpoint,status_key",
    [
        (
            blueprint,
            "/restricted_services_status_cloudfunctions",
            "cloudfunctions_restricted",
        ),
        (blueprint, "/restricted_services_status_dialogflow", "dialogflow_restricted"),
    ],
    indirect=["app"],
)
def test_restricted_services_status_cloudfunctions_success(app, endpoint, status_key):
    """Test restricted services status, success."""
    with patch.object(
        get_token, "get_token", return_value={"access_token": "MOCK_ACCESS_TOKEN"}
    ):
        with patch.object(
            su,
            "get_access_policy_name",
            return_value={"access_policy_name": "MOCK_ACCESS_POLICY_NAME"},
        ):
            with patch.object(
                su,
                "get_restricted_services_status",
                return_value={status_key: "SUCCESS"},
            ):
                return_value = get_result(app, endpoint)
    assert_response(return_value, 200, endpoint, json.dumps({"status": "SUCCESS"}))


@pytest.mark.hermetic
@pytest.mark.parametrize(
    "app,endpoint",
    [
        (blueprint, "/webhook_ingress_internal_only_status"),
        (blueprint, "/webhook_access_allow_unauthenticated_status"),
    ],
    indirect=["app"],
)
def test_webhook_no_function(app, endpoint):
    """Test webhook, function does not exist"""
    with patch.object(
        get_token, "get_token", return_value={"access_token": "MOCK_ACCESS_TOKEN"}
    ):
        with patch.object(
            su, "check_function_exists", return_value={"response": "MOCK_RESPONSE"}
        ):
            return_value = get_result(
                app, endpoint, mock_region=True, mock_webhook_name=True
            )
    assert_response(return_value, 200, endpoint, "MOCK_RESPONSE")


@pytest.mark.hermetic
@pytest.mark.parametrize("app", [blueprint], indirect=["app"])
def test_webhook_ingress_internal_only_status_api_error(
    app,
):
    """Test /webhook_ingress_internal_only_status, api error"""
    endpoint = "/webhook_ingress_internal_only_status"
    with patch.object(
        get_token, "get_token", return_value={"access_token": "MOCK_ACCESS_TOKEN"}
    ):
        with patch.object(su, "check_function_exists", return_value={"status": "OK"}):
            with patch.object(requests, "get", return_value=MockReturnObject(500, {})):
                return_value = get_result(
                    app, endpoint, mock_region=True, mock_webhook_name=True
                )
    assert_response(return_value, 500, endpoint)


@pytest.mark.hermetic
@pytest.mark.parametrize(
    "app,ingress_settings,status",
    [
        (blueprint, "ALLOW_INTERNAL_ONLY", True),
        (blueprint, "ALLOW_ALL", False),
        (blueprint, "ALLOW_INTERNAL_AND_GCLB", True),
    ],
    indirect=["app"],
)
def test_webhook_ingress_internal_only_status_success(app, ingress_settings, status):
    """Test /webhook_ingress_internal_only_status, success."""
    endpoint = "/webhook_ingress_internal_only_status"
    with patch.object(
        get_token, "get_token", return_value={"access_token": "MOCK_ACCESS_TOKEN"}
    ):
        with patch.object(su, "check_function_exists", return_value={"status": "OK"}):
            with patch.object(
                requests,
                "get",
                return_value=MockReturnObject(
                    200, {"ingressSettings": ingress_settings}
                ),
            ):
                return_value = get_result(
                    app, endpoint, mock_region=True, mock_webhook_name=True
                )
    assert_response(return_value, 200, endpoint, json.dumps({"status": status}))


@pytest.mark.hermetic
@pytest.mark.parametrize(
    "app,status,return_value,expected,expected_status",
    [
        (
            blueprint,
            403,
            {
                "error": {
                    "status": "PERMISSION_DENIED",
                    "message": "Permission 'cloudfunctions.functions.getIamPolicy' denied",
                }
            },
            {"status": "BLOCKED", "reason": "PERMISSION_DENIED"},
            200,
        ),
        (
            blueprint,
            403,
            {
                "error": {
                    "status": "PERMISSION_DENIED",
                    "message": "Cloud Functions API has not been used in project",
                }
            },
            {"status": "BLOCKED", "reason": "CLOUDFUNCTIONS_API_DISABLED"},
            200,
        ),
        (
            blueprint,
            403,
            {
                "error": {
                    "status": "PERMISSION_DENIED",
                    "message": "MOCK_MESSAGE",
                    "details": [],
                }
            },
            {
                "error": {
                    "status": "PERMISSION_DENIED",
                    "message": "MOCK_MESSAGE",
                    "details": [],
                }
            },
            500,
        ),
        (
            blueprint,
            403,
            {
                "error": {
                    "status": "PERMISSION_DENIED",
                    "message": "MOCK_MESSAGE",
                    "details": [{"violations": [{"type": "VPC_SERVICE_CONTROLS"}]}],
                }
            },
            {"status": "BLOCKED", "reason": "VPC_SERVICE_CONTROLS"},
            200,
        ),
        (blueprint, 500, {}, None, 500),
    ],
    indirect=["app"],
)
def test_webhook_access_allow_unauthenticated_status_api_error(
    app,
    status,
    return_value,
    expected,
    expected_status,
):
    """Test /webhook_access_allow_unauthenticated_status, api error"""
    endpoint = "/webhook_access_allow_unauthenticated_status"
    with patch.object(
        get_token, "get_token", return_value={"access_token": "MOCK_ACCESS_TOKEN"}
    ):
        with patch.object(su, "check_function_exists", return_value={"status": "OK"}):
            with patch.object(
                requests, "get", return_value=MockReturnObject(status, return_value)
            ):
                return_value = get_result(
                    app, endpoint, mock_region=True, mock_webhook_name=True
                )
    assert_response(
        return_value,
        expected_status,
        endpoint,
        json.dumps(expected) if expected is not None else None,
    )


@pytest.mark.hermetic
@pytest.mark.parametrize(
    "app,policy_dict,status",
    [
        (blueprint, {}, True),
        (blueprint, {"bindings": []}, True),
        (blueprint, {"bindings": [{"members": []}]}, True),
        (
            blueprint,
            {
                "bindings": [
                    {"members": ["allUsers"], "role": "roles/cloudfunctions.invoker"}
                ]
            },
            False,
        ),
        (
            blueprint,
            {"bindings": [{"members": ["allUsers"], "role": "MOCK_ROLE"}]},
            True,
        ),
    ],
    indirect=["app"],
)
def test_webhook_access_allow_unauthenticated_status_success(
    app,
    policy_dict,
    status,
):
    """Test /webhook_access_allow_unauthenticated_status, success"""
    endpoint = "/webhook_access_allow_unauthenticated_status"
    with patch.object(
        get_token, "get_token", return_value={"access_token": "MOCK_ACCESS_TOKEN"}
    ):
        with patch.object(su, "check_function_exists", return_value={"status": "OK"}):
            with patch.object(
                requests, "get", return_value=MockReturnObject(200, policy_dict)
            ):
                return_value = get_result(
                    app, endpoint, mock_region=True, mock_webhook_name=True
                )
    assert_response(
        return_value,
        200,
        endpoint,
        json.dumps({"status": status}),
    )


@pytest.mark.hermetic
@pytest.mark.parametrize(
    "app,return_value,expected,region",
    [
        (blueprint, {"response": "MOCK_RESPONSE"}, "MOCK_RESPONSE", "us-central1"),
        (
            blueprint,
            {"data": []},
            json.dumps(
                {
                    "status": "BLOCKED",
                    "reason": "AGENT_NOT_FOUND",
                }
            ),
            "us-central1",
        ),
        (
            blueprint,
            {"data": []},
            json.dumps({"status": "BLOCKED", "reason": "UNKNOWN_REGION"}),
            "BAD_REGION",
        ),
    ],
    indirect=["app"],
)
def test_service_directory_webhook_fulfillment_status_no_agent(
    app, return_value, expected, region
):
    """Test /service_directory_webhook_fulfillment_status, no agent"""
    endpoint = "/service_directory_webhook_fulfillment_status"
    with patch.object(
        get_token, "get_token", return_value={"access_token": "MOCK_ACCESS_TOKEN"}
    ):
        with patch.object(su, "get_agents", return_value=return_value):
            return_value = get_result(app, endpoint, mock_region=region)
    assert_response(
        return_value,
        200,
        endpoint,
        expected,
    )


@pytest.mark.hermetic
@pytest.mark.parametrize(
    "app,region,expected",
    [
        (blueprint, "us-central1", "MOCK_RESPONSE"),
        (
            blueprint,
            "MOCK_REGION",
            json.dumps({"status": "BLOCKED", "reason": "UNKNOWN_REGION"}),
        ),
    ],
    indirect=["app"],
)
def test_service_directory_webhook_fulfillment_status_no_webhook(app, region, expected):
    """Test /service_directory_webhook_fulfillment_status, no webhook"""
    endpoint = "/service_directory_webhook_fulfillment_status"
    with patch.object(
        get_token, "get_token", return_value={"access_token": "MOCK_ACCESS_TOKEN"}
    ):
        with patch.object(
            su,
            "get_agents",
            return_value={"data": {"Telecommunications": {"name": "MOCK_AGENT_NAME"}}},
        ):
            with patch.object(
                su, "get_webhooks", return_value={"response": "MOCK_RESPONSE"}
            ):
                return_value = get_result(app, endpoint, mock_region=region)
    assert_response(
        return_value,
        200,
        endpoint,
        expected,
    )


@pytest.mark.hermetic
@pytest.mark.parametrize(
    "app,webhook_dict,expected,region",
    [
        (blueprint, {}, {"status": False}, "us-central1"),
        (blueprint, {"serviceDirectory": "MOCK_DATA"}, {"status": True}, "us-central1"),
        (
            blueprint,
            {"serviceDirectory": "MOCK_DATA"},
            {
                "status": "BLOCKED",
                "reason": "UNKNOWN_REGION",
            },
            "MOCK_REGION",
        ),
    ],
    indirect=["app"],
)
def test_service_directory_webhook_fulfillment_status_success(
    app, webhook_dict, expected, region
):  # pylint: disable=redefined-outer-name
    """Test /service_directory_webhook_fulfillment_status, success"""
    endpoint = "/service_directory_webhook_fulfillment_status"
    with patch.object(
        get_token, "get_token", return_value={"access_token": "MOCK_ACCESS_TOKEN"}
    ):
        with patch.object(
            su,
            "get_agents",
            return_value={"data": {"Telecommunications": {"name": "MOCK_AGENT_NAME"}}},
        ):
            with patch.object(
                su,
                "get_webhooks",
                return_value={"data": {"cxPrebuiltAgentsTelecom": webhook_dict}},
            ):
                return_value = get_result(app, endpoint, mock_region=region)
    assert_response(
        return_value,
        200,
        endpoint,
        json.dumps(expected),
    )
