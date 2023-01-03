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

"""Tests for update_blueprint.py."""

import json

import analytics_utilities as au
import pytest
import requests
import status_utilities as su
import update_utilities as uu
from conftest import MOCK_DOMAIN, MockReturnObject
from conftest import assert_response_ep as assert_response
from conftest import generate_mock_register_action
from mock import patch
from update_blueprint import update as blueprint


def get_result(
    app,
    endpoint,
    json_data=None,
    query_string=None,
):
    """Helper function to get result from a test client."""
    json_data = {} if json_data is None else json_data
    query_string = {} if query_string is None else query_string
    with app.test_client() as curr_client:
        return curr_client.post(
            endpoint,
            base_url=f"https://{MOCK_DOMAIN}",
            json=json_data,
            query_string=query_string,
        )


@pytest.mark.hermetic
@pytest.mark.parametrize(
    "app,endpoint",
    [
        (blueprint, "/update_webhook_access"),
        (blueprint, "/update_webhook_ingress"),
        (blueprint, "/update_security_perimeter_cloudfunctions"),
        (blueprint, "/update_security_perimeter_dialogflow"),
        (blueprint, "/update_service_directory_webhook_fulfillment"),
    ],
    indirect=["app"],
)
@patch.object(su, "get_token_and_project", return_value={"response": "MOCK_RESPONSE"})
def test_endpoints_bad_token(get_token_mock, app, endpoint):
    """Test endpoints, bad token"""
    with patch.object(
        au, "register_action", new_callable=generate_mock_register_action
    ):
        return_value = get_result(app, endpoint)
    assert_response(return_value, 200, endpoint, "MOCK_RESPONSE")
    get_token_mock.assert_called_once()


@pytest.mark.hermetic
@pytest.mark.parametrize(
    "app,endpoint",
    [
        (blueprint, "/update_webhook_access"),
        (blueprint, "/update_webhook_ingress"),
    ],
    indirect=["app"],
)
@patch.object(
    su,
    "get_token_and_project",
    return_value={"token": "MOCK_ACCESS_TOKEN", "project_id": "MOCK_PROJECT_ID"},
)
@patch.object(
    requests,
    "get",
    return_value=MockReturnObject(500, text="MOCK_RESPONSE"),
)
def test_update_webhook_access_cloudfunctions_error(
    mock_requests, mock_get_token, app, endpoint
):
    """Test update_webhook endpoints, bad cloudfunctions api access."""
    return_value = get_result(
        app,
        endpoint,
        json_data={"status": True},
        query_string={
            "region": "MOCK_REGION",
            "webhook_name": "MOCK_WEBHOOK_NAME",
        },
    )
    assert_response(return_value, 500, endpoint, json.dumps({"error": "MOCK_RESPONSE"}))
    mock_get_token.assert_called_once()
    mock_requests.assert_called_once()


@pytest.mark.hermetic
@pytest.mark.parametrize(
    "app,policy_dict,status",
    [
        (blueprint, {}, True),
        (blueprint, {"bindings": []}, True),
        (
            blueprint,
            {"bindings": [{"role": "MOCK_ROLE", "members": ["allUsers"]}]},
            True,
        ),
        (
            blueprint,
            {
                "bindings": [
                    {"role": "roles/cloudfunctions.invoker", "members": ["MOCK_USER"]}
                ]
            },
            True,
        ),
        (
            blueprint,
            {
                "bindings": [
                    {"role": "roles/cloudfunctions.invoker", "members": ["allUsers"]}
                ]
            },
            False,
        ),
    ],
    indirect=["app"],
)
@patch.object(
    su,
    "get_token_and_project",
    return_value={"token": "MOCK_ACCESS_TOKEN", "project_id": "MOCK_PROJECT_ID"},
)
def test_update_webhook_access_no_change_needed(
    mock_get_token,
    app,
    policy_dict,
    status,
):
    "Test update_webhook_access, no change needed."
    endpoint = "/update_webhook_access"
    with patch.object(requests, "get", return_value=MockReturnObject(200, policy_dict)):
        return_value = get_result(
            app,
            endpoint,
            json_data={"status": status},
            query_string={
                "region": "MOCK_REGION",
                "webhook_name": "MOCK_WEBHOOK_NAME",
            },
        )
    assert_response(return_value, 200, endpoint)
    mock_get_token.assert_called_once()


@pytest.mark.hermetic
@pytest.mark.parametrize(
    "app,policy_dict,status,post_return_code",
    [
        (blueprint, {}, False, 500),
        (blueprint, {"bindings": []}, False, 500),
        (
            blueprint,
            {"bindings": [{"role": "MOCK_ROLE", "members": ["allUsers"]}]},
            False,
            500,
        ),
        (
            blueprint,
            {
                "bindings": [
                    {"role": "roles/cloudfunctions.invoker", "members": ["MOCK_USER"]}
                ]
            },
            False,
            500,
        ),
        (
            blueprint,
            {
                "bindings": [
                    {"role": "roles/cloudfunctions.invoker", "members": ["allUsers"]}
                ]
            },
            True,
            500,
        ),
        (blueprint, {}, False, 200),
        (blueprint, {"bindings": []}, False, 200),
        (
            blueprint,
            {"bindings": [{"role": "MOCK_ROLE", "members": ["allUsers"]}]},
            False,
            200,
        ),
        (
            blueprint,
            {
                "bindings": [
                    {"role": "roles/cloudfunctions.invoker", "members": ["MOCK_USER"]}
                ]
            },
            False,
            200,
        ),
        (
            blueprint,
            {
                "bindings": [
                    {"role": "roles/cloudfunctions.invoker", "members": ["allUsers"]}
                ]
            },
            True,
            200,
        ),
    ],
    indirect=["app"],
)
@patch.object(
    su,
    "get_token_and_project",
    return_value={"token": "MOCK_ACCESS_TOKEN", "project_id": "MOCK_PROJECT_ID"},
)
@patch.object(au, "register_action", new_callable=generate_mock_register_action)
def test_update_webhook_access_change_needed(  # pylint: disable=too-many-arguments
    mock_register_action,
    mock_get_token,
    app,
    policy_dict,
    status,
    post_return_code,
):
    "Test update_webhook_access, change needed."
    endpoint = "/update_webhook_access"
    with patch.object(
        requests, "get", return_value=MockReturnObject(200, policy_dict)
    ) as mock_request_get:
        with patch.object(
            requests,
            "post",
            return_value=MockReturnObject(post_return_code, text="MOCK_RESPONSE"),
        ) as mock_request_post:
            return_value = get_result(
                app,
                endpoint,
                json_data={"status": status},
                query_string={
                    "region": "MOCK_REGION",
                    "webhook_name": "MOCK_WEBHOOK_NAME",
                },
            )
    assert_response(
        return_value, post_return_code, endpoint, json.dumps({"error": "MOCK_RESPONSE"})
    )
    mock_get_token.assert_called_once()
    mock_request_post.assert_called_once()
    mock_request_get.assert_called_once()
    if status is True and post_return_code == 200:
        mock_register_action.assert_called_once()


@pytest.mark.hermetic
@patch.object(
    su,
    "get_token_and_project",
    return_value={"token": "MOCK_ACCESS_TOKEN", "project_id": "MOCK_PROJECT_ID"},
)
@pytest.mark.parametrize(
    "app,status,ingress_settings",
    [
        (blueprint, True, "ALLOW_INTERNAL_ONLY"),
        (blueprint, False, "ALLOW_ALL"),
    ],
    indirect=["app"],
)
def test_update_webhook_ingress_no_change_needed(
    mock_get_token,
    app,
    status,
    ingress_settings,
):
    """Test /update_webhook_ingress, no change needed."""
    endpoint = "/update_webhook_ingress"
    with patch.object(
        requests,
        "get",
        return_value=MockReturnObject(200, {"ingressSettings": ingress_settings}),
    ) as mock_requests_get:
        return_value = get_result(
            app,
            endpoint,
            json_data={"status": status},
            query_string={
                "region": "MOCK_REGION",
                "webhook_name": "MOCK_WEBHOOK_NAME",
            },
        )
    assert_response(return_value, 200, endpoint)
    mock_get_token.assert_called_once()
    mock_requests_get.assert_called_once()


@pytest.mark.hermetic
@patch.object(
    su,
    "get_token_and_project",
    return_value={"token": "MOCK_ACCESS_TOKEN", "project_id": "MOCK_PROJECT_ID"},
)
@pytest.mark.parametrize(
    "app,status,ingress_settings,patch_return_code",
    [
        (blueprint, False, "ALLOW_INTERNAL_ONLY", 500),
        (blueprint, True, "ALLOW_ALL", 500),
        (blueprint, False, "ALLOW_INTERNAL_ONLY", 200),
        (blueprint, True, "ALLOW_ALL", 200),
    ],
    indirect=["app"],
)
@patch.object(au, "register_action", new_callable=generate_mock_register_action)
def test_update_webhook_ingress_change_needed(  # pylint: disable=too-many-arguments
    mock_register_action,
    mock_get_token,
    app,
    status,
    ingress_settings,
    patch_return_code,
):
    """Test /update_webhook_ingress, change needed."""
    endpoint = "/update_webhook_ingress"
    with patch.object(
        requests,
        "get",
        return_value=MockReturnObject(200, {"ingressSettings": ingress_settings}),
    ) as mock_requests_get:
        with patch.object(
            requests,
            "patch",
            return_value=MockReturnObject(
                patch_return_code, {"ingressSettings": ingress_settings}
            ),
        ) as mock_requests_patch:
            return_value = get_result(
                app,
                endpoint,
                json_data={"status": status},
                query_string={
                    "region": "MOCK_REGION",
                    "webhook_name": "MOCK_WEBHOOK_NAME",
                },
            )
    assert_response(return_value, patch_return_code, endpoint)
    mock_get_token.assert_called_once()
    mock_requests_get.assert_called_once()
    mock_requests_patch.assert_called_once()
    if patch_return_code == 200:
        mock_register_action.assert_called_once()


@pytest.mark.hermetic
@patch.object(
    uu,
    "update_security_perimeter",
    return_value="MOCK_RESPONSE",
)
@patch.object(au, "register_action", new_callable=generate_mock_register_action)
@pytest.mark.parametrize(
    "app,endpoint",
    [
        (blueprint, "/update_security_perimeter_cloudfunctions"),
        (blueprint, "/update_security_perimeter_dialogflow"),
    ],
    indirect=["app"],
)
def test_update_perimeter_bad_policy_name(
    mock_update_security_perimeter,
    mock_register_action,
    app,
    endpoint,
):
    """Test perimeter update methods, with bad policy names."""
    return_value = get_result(
        app,
        endpoint,
        query_string={"access_policy_title": "MOCK_ACCESS_POLICY_TITLE"},
    )
    assert_response(return_value, 200, endpoint, "MOCK_RESPONSE")
    mock_update_security_perimeter.assert_called_once()
    mock_register_action.assert_called_once()


@pytest.mark.hermetic
@pytest.mark.parametrize(
    "app,status",
    [
        (blueprint, True),
        (blueprint, False),
    ],
    indirect=["app"],
)
@patch.object(
    su,
    "get_token_and_project",
    return_value={"token": "MOCK_ACCESS_TOKEN", "project_id": "MOCK_PROJECT_ID"},
)
@patch.object(
    su,
    "get_agents",
    return_value={"response": "MOCK_RESPONSE"},
)
def test_update_service_directory_webhook_fulfillment_bad_agent(
    mock_get_token_and_project,
    mock_get_agent,
    app,
    status,
):
    """Test update_service_directory_webhook_fulfillment, bad agent."""
    endpoint = "/update_service_directory_webhook_fulfillment"
    return_value = get_result(
        app,
        endpoint,
        query_string={
            "region": "us-central1",
            "bucket": "MOCK_BUCKET_NAME",
            "webhook_name": "MOCK_WEBHOOK_NAME",
        },
        json_data={
            "status": status,
        },
    )
    assert_response(return_value, 200, endpoint, "MOCK_RESPONSE")
    mock_get_token_and_project.assert_called_once()
    mock_get_agent.assert_called_once()


@pytest.mark.hermetic
@pytest.mark.parametrize(
    "app,status",
    [
        (blueprint, True),
        (blueprint, False),
    ],
    indirect=["app"],
)
@patch.object(
    su,
    "get_token_and_project",
    return_value={"token": "MOCK_ACCESS_TOKEN", "project_id": "MOCK_PROJECT_ID"},
)
@patch.object(
    su,
    "get_agents",
    return_value={"data": {"Telecommunications": {"name": "MOCK_NAME"}}},
)
@patch.object(
    su,
    "get_webhooks",
    return_value={"response": "MOCK_RESPONSE"},
)
def test_update_service_directory_webhook_fulfillment_bad_webhook(
    mock_get_token_and_project,
    mock_get_agents,
    mock_get_webhooks,
    app,
    status,
):
    """Test update_service_directory_webhook_fulfillment, bad webhook."""
    endpoint = "/update_service_directory_webhook_fulfillment"
    return_value = get_result(
        app,
        endpoint,
        query_string={
            "region": "us-central1",
            "bucket": "MOCK_BUCKET_NAME",
            "webhook_name": "MOCK_WEBHOOK_NAME",
        },
        json_data={
            "status": status,
        },
    )
    assert_response(return_value, 200, endpoint, "MOCK_RESPONSE")
    mock_get_token_and_project.assert_called_once()
    mock_get_agents.assert_called_once()
    mock_get_webhooks.assert_called_once()


@pytest.mark.hermetic
@pytest.mark.parametrize(
    "app,status,patch_code",
    [
        (blueprint, True, 500),
        (blueprint, True, 200),
        (blueprint, False, 500),
        (blueprint, False, 200),
    ],
    indirect=["app"],
)
@patch.object(
    su,
    "get_token_and_project",
    return_value={"token": "MOCK_ACCESS_TOKEN", "project_id": "MOCK_PROJECT_ID"},
)
@patch.object(
    su,
    "get_agents",
    return_value={"data": {"Telecommunications": {"name": "MOCK_AGENT_NAME"}}},
)
@patch.object(
    su,
    "get_webhooks",
    return_value={"data": {"cxPrebuiltAgentsTelecom": {"name": "MOCK_WEBHOOK_NAME"}}},
)
@patch.object(
    uu,
    "get_cert",
    return_value="MOCK_CERT".encode(),
)
@patch.object(au, "register_action", new_callable=generate_mock_register_action)
def test_update_service_directory_webhook_fulfillment(  # pylint: disable=too-many-arguments
    mock_register_action,
    mock_get_cert,
    mock_get_webhooks,
    mock_get_agents,
    mock_get_token_and_project,
    app,
    status,
    patch_code,
):
    """Test update_service_directory_webhook_fulfillment."""
    endpoint = "/update_service_directory_webhook_fulfillment"
    with patch.object(
        requests,
        "patch",
        return_value=MockReturnObject(patch_code, text="MOCK_RESPONSE"),
    ) as mock_patch:
        return_value = get_result(
            app,
            endpoint,
            query_string={
                "region": "us-central1",
                "bucket": "MOCK_BUCKET_NAME",
                "webhook_name": "MOCK_WEBHOOK_NAME",
            },
            json_data={
                "status": status,
            },
        )
    assert_response(
        return_value, patch_code, endpoint, json.dumps({"error": "MOCK_RESPONSE"})
    )
    mock_get_token_and_project.assert_called_once()
    mock_get_agents.assert_called_once()
    mock_get_webhooks.assert_called_once()
    mock_patch.assert_called_once()
    if status:
        mock_get_cert.assert_called_once()
        if patch_code == 200:
            mock_register_action.assert_called_once()


@pytest.mark.hermetic
@patch.object(
    su,
    "get_token_and_project",
    return_value={"token": "MOCK_ACCESS_TOKEN", "project_id": "MOCK_PROJECT_ID"},
)
@pytest.mark.parametrize("app", [blueprint], indirect=["app"])
def test_update_service_directory_webhook_fulfillment_bad_region(
    mock_get_token_and_project,
    app,
):
    """Test bad region provided to /update_service_directory_webhook_fulfillment"""
    endpoint = "/update_service_directory_webhook_fulfillment"
    return_value = get_result(
        app,
        endpoint,
        query_string={
            "region": "BAD_REGION",
            "bucket": "MOCK_BUCKET_NAME",
            "webhook_name": "MOCK_WEBHOOK_NAME",
        },
        json_data={
            "status": "MOCK_STATUS",
        },
    )
    assert_response(
        return_value,
        200,
        endpoint,
        json.dumps({"status": "BLOCKED", "reason": "UNKNOWN_REGION"}),
    )
    mock_get_token_and_project.assert_called_once()
