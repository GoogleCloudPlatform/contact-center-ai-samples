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

"""Module for testing status_utilities.py."""

import get_token
import pytest
import requests
import status_utilities as su
from conftest import MockReturnObject, assert_response
from mock import patch


@pytest.mark.hermetic
def test_get_project_number():
    """Test get_project_number function."""
    with patch.object(
        requests,
        "get",
        return_value=MockReturnObject(200, {"projectNumber": "MOCK_PROJECT_NUMBER"}),
    ):
        result = su.get_project_number("MOCK_TOKEN", "MOCK_PROJECT_ID")
    assert result == {"project_number": "MOCK_PROJECT_NUMBER"}


@pytest.mark.hermetic
def test_get_project_number_no_project():
    """Test get_project_number function."""
    with patch.object(requests, "get", return_value=MockReturnObject(200, {})):
        result = su.get_project_number("MOCK_TOKEN", "MOCK_PROJECT_ID")
    assert_response(result, 200, {"status": "BLOCKED", "reason": "NO_PROJECT"})


@pytest.mark.hermetic
@pytest.mark.parametrize("title", [None, False])
def test_get_access_policy_name_no_policy(title):
    """Test get_access_policy_name function, no policy given."""
    result = su.get_access_policy_name("MOCK_TOKEN", title, "MOCK_PROJECT_ID")
    assert_response(result, 200, {"status": "BLOCKED", "reason": "NO_ACCESS_POLICY"})


@pytest.mark.hermetic
def test_get_access_policy_name_bad_token():
    """Test get_access_policy_name, bad token."""
    with patch.object(
        requests,
        "post",
        return_value=MockReturnObject(401, {"error": {"status": "UNAUTHENTICATED"}}),
    ):
        result = su.get_access_policy_name(
            "MOCK_TOKEN", "MOCK_PROJECT_TITLE", "MOCK_PROJECT_ID"
        )
        assert_response(result, 200, {"status": "BLOCKED", "reason": "UNKNOWN_STATUS"})


@pytest.mark.hermetic
def test_get_access_policy_name_no_organization():
    """Test get_access_policy_name, bad organization."""
    with patch.object(requests, "post", return_value=MockReturnObject(200, {})):
        result = su.get_access_policy_name(
            "MOCK_TOKEN", "MOCK_PROJECT_TITLE", "MOCK_PROJECT_ID"
        )
        assert_response(result, 200, {"status": "BLOCKED", "reason": "NO_ORGANIZATION"})


@pytest.mark.hermetic
def test_get_access_policy_name_bad_project():
    """Test get_access_policy_name, bad project."""
    with patch.object(
        requests,
        "post",
        return_value=MockReturnObject(
            200,
            {
                "ancestor": [
                    {"resourceId": {"type": "organization", "id": "MOCK_ANCESTOR_ID"}}
                ]
            },
        ),
    ):
        result = su.get_access_policy_name(
            "MOCK_TOKEN", "MOCK_PROJECT_TITLE", "MOCK_PROJECT_ID"
        )
        assert_response(result, 200, {"status": "BLOCKED", "reason": "NO_PROJECT"})


@pytest.mark.hermetic
def test_get_access_policy_name_no_policy_found():
    """Test get_access_policy_name, bad policy configured."""
    with patch.object(
        requests,
        "post",
        return_value=MockReturnObject(
            200,
            {
                "ancestor": [
                    {"resourceId": {"type": "organization", "id": "MOCK_ANCESTOR_ID"}}
                ]
            },
        ),
    ):
        with patch.object(
            su,
            "get_project_number",
            return_value={"project_number": "MOCK_PROJECT_NUMBER"},
        ):
            result = su.get_access_policy_name(
                "MOCK_TOKEN", "MOCK_PROJECT_TITLE", "MOCK_PROJECT_ID"
            )
            assert_response(
                result, 200, {"status": "BLOCKED", "reason": "POLICY_NOT_FOUND"}
            )


@pytest.mark.hermetic
def test_get_access_policy_name():
    """Test get_access_policy_name, found the policy."""
    with patch.object(
        requests,
        "post",
        return_value=MockReturnObject(
            200,
            {
                "ancestor": [
                    {"resourceId": {"type": "organization", "id": "MOCK_ANCESTOR_ID"}}
                ]
            },
        ),
    ):
        with patch.object(
            su,
            "get_project_number",
            return_value={"project_number": "MOCK_PROJECT_NUMBER"},
        ):
            with patch.object(
                requests,
                "get",
                return_value=MockReturnObject(
                    200,
                    {
                        "accessPolicies": [
                            {
                                "title": "MOCK_PROJECT_TITLE",
                                "scopes": ["projects/MOCK_PROJECT_NUMBER"],
                                "name": "MOCK_ACCESS_POLICY",
                            }
                        ]
                    },
                ),
            ):
                result = su.get_access_policy_name(
                    "MOCK_TOKEN", "MOCK_PROJECT_TITLE", "MOCK_PROJECT_ID"
                )
                assert result == {"access_policy_name": "MOCK_ACCESS_POLICY"}


@pytest.mark.hermetic
def test_get_service_perimeter_data_uri_api():
    """Test get service perimieter, ACCESS_CONTEXT_MANAGER_API_DISABLED"""
    with patch.object(
        requests,
        "get",
        return_value=MockReturnObject(
            401,
            {
                "error": {
                    "status": "PERMISSION_DENIED",
                    "message": "Access Context Manager API has not been used in project",
                }
            },
        ),
    ):
        result = su.get_service_perimeter_data_uri(
            "MOCK_TOKEN", "MOCK_PROJECT_ID", "MOCK/MOCK_ACCESS_POLICY"
        )
        assert_response(
            result,
            200,
            {"status": "BLOCKED", "reason": "ACCESS_CONTEXT_MANAGER_API_DISABLED"},
        )


@pytest.mark.hermetic
def test_get_service_perimeter_data_uri_permission():
    """Test get service perimieter, permission denied"""
    with patch.object(
        requests,
        "get",
        return_value=MockReturnObject(
            401,
            {
                "error": {
                    "status": "PERMISSION_DENIED",
                    "message": "MOCK_MESSAGE",
                }
            },
        ),
    ):
        result = su.get_service_perimeter_data_uri(
            "MOCK_TOKEN", "MOCK_PROJECT_ID", "MOCK/MOCK_ACCESS_POLICY"
        )
        assert_response(
            result, 200, {"status": "BLOCKED", "reason": "PERMISSION_DENIED"}
        )


@pytest.mark.hermetic
def test_get_service_perimeter_data_uri_unknown():
    """Test get service perimieter, unknown error."""
    with patch.object(
        requests,
        "get",
        return_value=MockReturnObject(
            500,
            {
                "error": {
                    "status": "UNKNOWN",
                }
            },
        ),
    ):
        result = su.get_service_perimeter_data_uri(
            "MOCK_TOKEN", "MOCK_PROJECT_ID", "MOCK/MOCK_ACCESS_POLICY"
        )
        assert_response(result, 500, {"error": {"status": "UNKNOWN"}})


@pytest.mark.hermetic
def test_get_service_perimeter_data_uri_no_perimeter():
    """Test get service perimieter, no perimeter."""
    with patch.object(requests, "get", return_value=MockReturnObject(200, {})):
        result = su.get_service_perimeter_data_uri(
            "MOCK_TOKEN", "MOCK_PROJECT_ID", "MOCK/MOCK_ACCESS_POLICY"
        )
        assert_response(
            result, 200, {"status": "BLOCKED", "reason": "PERIMETER_NOT_FOUND"}
        )


@pytest.mark.hermetic
def test_get_service_perimeter_data_uri_yes_perimeter():
    """Test get service perimieter, success"""
    with patch.object(
        requests,
        "get",
        return_value=MockReturnObject(
            200,
            {
                "servicePerimeters": [
                    {
                        "title": "MOCK_PERIMETER_TITLE",
                        "name": "MOCK_PERIMETER_NAME",
                    }
                ]
            },
        ),
    ):
        result = su.get_service_perimeter_data_uri(
            "MOCK_TOKEN",
            "MOCK_PROJECT_ID",
            "MOCK/MOCK_ACCESS_POLICY",
            perimeter_title="MOCK_PERIMETER_TITLE",
        )
        assert result == {
            "uri": "https://accesscontextmanager.googleapis.com/v1/MOCK_PERIMETER_NAME",
        }


@pytest.mark.hermetic
def test_get_service_perimeter_status_bad_perimeter():
    """Test get_service_perimeter_status, bad service perimeter"""
    with patch.object(
        su,
        "get_service_perimeter_data_uri",
        return_value={"response": "MOCK_ERROR_RESPONSE"},
    ):
        result = su.get_service_perimeter_status(
            "MOCK_TOKEN", "MOCK_PROJECT_ID", "MOCK/MOCK_ACCESS_POLICY"
        )
        assert result == {"response": "MOCK_ERROR_RESPONSE"}


@pytest.mark.hermetic
def test_get_service_perimeter_status_api_disabled():
    """Test get_service_perimeter_status, api disabled"""
    with patch.object(
        su,
        "get_service_perimeter_data_uri",
        return_value={"uri": "http://MOCK_URI"},
    ):
        with patch.object(
            requests,
            "get",
            return_value=MockReturnObject(
                401,
                {
                    "error": {
                        "status": "PERMISSION_DENIED",
                        "message": "Access Context Manager API has not been used in project",
                    }
                },
            ),
        ):
            result = su.get_service_perimeter_status(
                "MOCK_TOKEN", "MOCK_PROJECT_ID", "MOCK/MOCK_ACCESS_POLICY"
            )
            assert_response(
                {"response": result},
                200,
                {"status": "BLOCKED", "reason": "ACCESS_CONTEXT_MANAGER_API_DISABLED"},
            )


@pytest.mark.hermetic
def test_get_service_perimeter_status_permission_denied():
    """Test get_service_perimeter_status, permission denied"""
    with patch.object(
        su,
        "get_service_perimeter_data_uri",
        return_value={"uri": "http://MOCK_URI"},
    ):
        with patch.object(
            requests,
            "get",
            return_value=MockReturnObject(
                401,
                {
                    "error": {
                        "status": "PERMISSION_DENIED",
                        "message": "MOCK_ERROR_MESSAGE",
                    }
                },
            ),
        ):
            result = su.get_service_perimeter_status(
                "MOCK_TOKEN", "MOCK_PROJECT_ID", "MOCK/MOCK_ACCESS_POLICY"
            )
            assert_response(
                result, 200, {"status": "BLOCKED", "reason": "PERMISSION_DENIED"}
            )


@pytest.mark.hermetic
def test_get_service_perimeter_status_unknown_error():
    """Test get_service_perimeter_status, unknown error"""
    with patch.object(
        su,
        "get_service_perimeter_data_uri",
        return_value={"uri": "http://MOCK_URI"},
    ):
        with patch.object(
            requests,
            "get",
            return_value=MockReturnObject(
                500,
                {
                    "error": {
                        "status": "UNKNOWN",
                    }
                },
            ),
        ):
            result = su.get_service_perimeter_status(
                "MOCK_TOKEN", "MOCK_PROJECT_ID", "MOCK/MOCK_ACCESS_POLICY"
            )
            assert_response(result, 500, {"error": {"status": "UNKNOWN"}})


@pytest.mark.hermetic
def test_get_service_perimeter_status_success():
    """Test get_service_perimeter_status, success"""
    with patch.object(
        su,
        "get_service_perimeter_data_uri",
        return_value={"uri": "http://MOCK_URI"},
    ):
        with patch.object(
            requests, "get", return_value=MockReturnObject(200, ["MOCK_SUCCESS"])
        ):
            result = su.get_service_perimeter_status(
                "MOCK_TOKEN", "MOCK_PROJECT_ID", "MOCK/MOCK_ACCESS_POLICY"
            )
            assert result == ["MOCK_SUCCESS"]


@pytest.mark.hermetic
def test_get_restricted_services_status_bad_perimeter_status():
    """test get_restricted_services_status, bad response from service status"""

    with patch.object(
        su,
        "get_service_perimeter_status",
        return_value={"response": "MOCK_RESPONSE"},
    ):
        result = su.get_restricted_services_status(
            "MOCK_TOKEN", "MOCK_PROJECT_ID", "MOCK/MOCK_ACCESS_POLICY"
        )
        assert result == {"response": "MOCK_RESPONSE"}


@pytest.mark.hermetic
@pytest.mark.parametrize(
    "status,expected",
    [
        (
            {},
            {
                "cloudfunctions_restricted": False,
                "dialogflow_restricted": False,
            },
        ),
        (
            {"restrictedServices": []},
            {
                "cloudfunctions_restricted": False,
                "dialogflow_restricted": False,
            },
        ),
        (
            {"restrictedServices": ["cloudfunctions.googleapis.com"]},
            {
                "cloudfunctions_restricted": True,
                "dialogflow_restricted": False,
            },
        ),
        (
            {"restrictedServices": ["dialogflow.googleapis.com"]},
            {
                "cloudfunctions_restricted": False,
                "dialogflow_restricted": True,
            },
        ),
        (
            {
                "restrictedServices": [
                    "cloudfunctions.googleapis.com",
                    "dialogflow.googleapis.com",
                ]
            },
            {
                "cloudfunctions_restricted": True,
                "dialogflow_restricted": True,
            },
        ),
    ],
)
def test_get_restricted_services_status_parameterize(status, expected):
    """test get_restricted_services_status."""
    with patch.object(
        su,
        "get_service_perimeter_status",
        return_value={"status": status},
    ):
        result = su.get_restricted_services_status(
            "MOCK_TOKEN", "MOCK_PROJECT_ID", "MOCK/MOCK_ACCESS_POLICY"
        )
        assert result == expected


@pytest.mark.hermetic
def test_check_function_exists_cloudfunctions_404():
    """Test check_function_exists, 404 error webhook not found"""
    with patch.object(
        requests,
        "get",
        return_value=MockReturnObject(404, {"error": {"status": "NOT_FOUND"}}),
    ):
        result = su.check_function_exists(
            "MOCK_TOKEN", "MOCK_PROJECT_ID", "MOCK_REGION", "MOCK_FUNCTION_NAME"
        )
        assert_response(
            result, 200, {"status": "BLOCKED", "reason": "WEBHOOK_NOT_FOUND"}
        )


@pytest.mark.hermetic
def test_check_function_exists_cloudfunctions_api_not_used():
    """Test check_function_exists, api not set up."""
    with patch.object(
        requests,
        "get",
        return_value=MockReturnObject(
            403,
            {
                "error": {
                    "message": "Cloud Functions API has not been used in project",
                }
            },
        ),
    ):
        result = su.check_function_exists(
            "MOCK_TOKEN", "MOCK_PROJECT_ID", "MOCK_REGION", "MOCK_FUNCTION_NAME"
        )
        assert_response(
            result, 200, {"status": "BLOCKED", "reason": "CLOUDFUNCTIONS_API_DISABLED"}
        )


@pytest.mark.hermetic
def test_check_function_exists_permission_denied_iam():
    """Test check_function_exists, iam issue."""
    with patch.object(
        requests,
        "get",
        return_value=MockReturnObject(
            403,
            {
                "error": {
                    "status": "PERMISSION_DENIED",
                    "message": "Permission 'cloudfunctions.functions.get' denied on resource",
                }
            },
        ),
    ):
        result = su.check_function_exists(
            "MOCK_TOKEN", "MOCK_PROJECT_ID", "MOCK_REGION", "MOCK_FUNCTION_NAME"
        )
        assert_response(
            result, 200, {"status": "BLOCKED", "reason": "PERMISSION_DENIED"}
        )


@pytest.mark.hermetic
def test_check_function_exists_permission_denied_vpc():
    """Test check_function_exists, vpc in place."""
    with patch.object(
        requests,
        "get",
        return_value=MockReturnObject(
            403,
            {
                "error": {
                    "details": [{"violations": [{"type": "VPC_SERVICE_CONTROLS"}]}],
                    "message": "MOCK_MESSAGE",
                    "status": "MOCK_STATUS",
                }
            },
        ),
    ):
        result = su.check_function_exists(
            "MOCK_TOKEN", "MOCK_PROJECT_ID", "MOCK_REGION", "MOCK_FUNCTION_NAME"
        )
        assert_response(
            result, 200, {"status": "BLOCKED", "reason": "VPC_SERVICE_CONTROLS"}
        )


@pytest.mark.hermetic
def test_check_function_exists_permission_denied_unknown_type():
    """Test check_function_exists, unknown error."""
    with patch.object(
        requests,
        "get",
        return_value=MockReturnObject(
            403,
            {
                "error": {
                    "details": [{"violations": [{"type": "UNKNOWN"}]}],
                    "message": "MOCK_MESSAGE",
                    "status": "MOCK_STATUS",
                }
            },
        ),
    ):
        result = su.check_function_exists(
            "MOCK_TOKEN", "MOCK_PROJECT_ID", "MOCK_REGION", "MOCK_FUNCTION_NAME"
        )
        assert_response(
            result,
            500,
            {
                "error": {
                    "details": [{"violations": [{"type": "UNKNOWN"}]}],
                    "message": "MOCK_MESSAGE",
                    "status": "MOCK_STATUS",
                }
            },
        )


@pytest.mark.hermetic
def test_check_function_exists_server_error():
    """Test check_function_exists, server error."""
    with patch.object(
        requests, "get", return_value=MockReturnObject(500, ["SERVER_ERROR"])
    ):
        result = su.check_function_exists(
            "MOCK_TOKEN", "MOCK_PROJECT_ID", "MOCK_REGION", "MOCK_FUNCTION_NAME"
        )
        assert_response(result, 500, ["SERVER_ERROR"])


@pytest.mark.hermetic
def test_check_function_exists_success():
    """Test check_function_exists, success."""
    with patch.object(requests, "get", return_value=MockReturnObject(200, {})):
        result = su.check_function_exists(
            "MOCK_TOKEN", "MOCK_PROJECT_ID", "MOCK_REGION", "MOCK_FUNCTION_NAME"
        )
        assert result == {"status": "OK"}


@pytest.mark.hermetic
def test_get_agents_bad_region():
    """Test get_agents, bad region provided."""
    result = su.get_agents("MOCK_TOKEN", "MOCK_PROJECT_ID", "BAD_REGION")
    assert_response(result, 200, {"status": "BLOCKED", "reason": "UNKNOWN_REGION"})


@pytest.mark.hermetic
def test_get_agents_api():
    """Test get_agents permission denied api not set up"""
    with patch.object(
        requests,
        "get",
        return_value=MockReturnObject(
            403,
            {
                "error": {
                    "status": "PERMISSION_DENIED",
                    "message": "Dialogflow API has not been used in project",
                }
            },
        ),
    ):
        result = su.get_agents("MOCK_TOKEN", "MOCK_PROJECT_ID", "us-central1")
        assert_response(
            result, 200, {"status": "BLOCKED", "reason": "DIALOGFLOW_API_DISABLED"}
        )


@pytest.mark.hermetic
def test_get_agents_iam():
    """Test get_agents permission denied iam permissions."""
    with patch.object(
        requests,
        "get",
        return_value=MockReturnObject(
            403,
            {
                "error": {
                    "status": "PERMISSION_DENIED",
                    "message": "Caller does not have required permission",
                }
            },
        ),
    ):
        result = su.get_agents("MOCK_TOKEN", "MOCK_PROJECT_ID", "us-central1")
        assert_response(
            result, 200, {"status": "BLOCKED", "reason": "WRONG_PERMISSION"}
        )


@pytest.mark.hermetic
def test_get_agents_vpc():
    """Test get_agents permission denied vpc."""
    with patch.object(
        requests,
        "get",
        return_value=MockReturnObject(
            403,
            {
                "error": {
                    "details": [{"violations": [{"type": "VPC_SERVICE_CONTROLS"}]}],
                    "message": "MOCK_MESSAGE",
                    "status": "MOCK_STATUS",
                }
            },
        ),
    ):
        result = su.get_agents("MOCK_TOKEN", "MOCK_PROJECT_ID", "us-central1")
        assert_response(
            result, 200, {"status": "BLOCKED", "reason": "VPC_SERVICE_CONTROLS"}
        )


@pytest.mark.hermetic
def test_get_agents_permissions_unknown():
    """Test get_agents permission denied permissions unknown."""
    with patch.object(
        requests,
        "get",
        return_value=MockReturnObject(
            403,
            data={
                "error": {
                    "status": "PERMISSION_DENIED",
                    "message": "UNKNOWN",
                    "details": [],
                }
            },
        ),
    ):
        result = su.get_agents("MOCK_TOKEN", "MOCK_PROJECT_ID", "us-central1")
        assert_response(
            result, 200, {"status": "BLOCKED", "reason": "PERMISSION_DENIED"}
        )


@pytest.mark.hermetic
def test_get_agents_server_error():
    """Test get_agents server error."""
    with patch.object(
        requests, "get", return_value=MockReturnObject(500, text="SERVER_ERROR")
    ):
        result = su.get_agents("MOCK_TOKEN", "MOCK_PROJECT_ID", "us-central1")
        assert_response(result, 500, {"error": "SERVER_ERROR"})


@pytest.mark.hermetic
def test_get_agents_not_found():
    """Test get_agents agent not found."""
    with patch.object(
        requests,
        "get",
        return_value=MockReturnObject(
            200,
            {},
        ),
    ):
        result = su.get_agents("MOCK_TOKEN", "MOCK_PROJECT_ID", "us-central1")
        assert_response(result, 200, {"status": "BLOCKED", "reason": "AGENT_NOT_FOUND"})


@pytest.mark.hermetic
def test_get_agents_potential_buggy_codepath():
    """I think this might be a buggy codepath, adding test for now to investigate later (TDD)."""
    with patch.object(
        requests,
        "get",
        return_value=MockReturnObject(
            200,
            {"error": "MOCK_ERROR"},
        ),
    ):
        result = su.get_agents("MOCK_TOKEN", "MOCK_PROJECT_ID", "us-central1")
        assert result is None


@pytest.mark.hermetic
def test_get_agents_success():
    """Test get_agents success."""
    with patch.object(
        requests,
        "get",
        return_value=MockReturnObject(
            200,
            {"agents": [{"displayName": "MOCK_AGENT_NAME"}]},
        ),
    ):
        result = su.get_agents("MOCK_TOKEN", "MOCK_PROJECT_ID", "us-central1")
    assert result == {"data": {"MOCK_AGENT_NAME": {"displayName": "MOCK_AGENT_NAME"}}}


@pytest.mark.hermetic
def test_get_webhooks_vpc():
    """Test get_webhooks, access error vpc"""
    with patch.object(
        requests,
        "get",
        return_value=MockReturnObject(
            403,
            {
                "error": {
                    "details": [{"violations": [{"type": "VPC_SERVICE_CONTROLS"}]}],
                    "message": "MOCK_MESSAGE",
                    "status": "MOCK_STATUS",
                }
            },
        ),
    ):
        result = su.get_webhooks(
            "MOCK_TOKEN", "MOCK_PROJECT_ID", "MOCK_PROJECT_ID", "MOCK_REGION"
        )
        assert_response(
            result, 200, {"status": "BLOCKED", "reason": "VPC_SERVICE_CONTROLS"}
        )


@pytest.mark.hermetic
def test_get_webhooks_server_error():
    """Test get_webhooks, access error vpc"""
    with patch.object(
        requests, "get", return_value=MockReturnObject(500, text="SERVER_ERROR")
    ):
        result = su.get_webhooks(
            "MOCK_TOKEN", "MOCK_PROJECT_ID", "MOCK_PROJECT_ID", "MOCK_REGION"
        )
        assert_response(result, 500, {"error": "SERVER_ERROR"})


@pytest.mark.hermetic
@patch.object(requests, "get", return_value=MockReturnObject(200, {}))
def test_get_webhooks_not_found(mock_requests_get):
    """Test get_webhooks, webhook not found"""
    result = su.get_webhooks(
        "MOCK_TOKEN", "MOCK_PROJECT_ID", "MOCK_PROJECT_ID", "MOCK_REGION"
    )
    assert_response(result, 200, {"status": "BLOCKED", "reason": "WEBHOOK_NOT_FOUND"})
    mock_requests_get.assert_called_once()


@pytest.mark.hermetic
def test_get_webhooks_success():
    """Test get_webhooks, success"""
    with patch.object(
        requests,
        "get",
        return_value=MockReturnObject(
            200,
            {"webhooks": [{"displayName": "MOCK_WEBHOOK_NAME"}]},
        ),
    ):
        result = su.get_webhooks(
            "MOCK_TOKEN", "MOCK_PROJECT_ID", "MOCK_PROJECT_ID", "MOCK_REGION"
        )
    assert result == {
        "data": {"MOCK_WEBHOOK_NAME": {"displayName": "MOCK_WEBHOOK_NAME"}}
    }


@pytest.mark.hermetic
@patch.object(get_token, "get_token", return_value={"response": "MOCK_RESPONSE"})
def test_get_token_and_project_bad_token(mock_get_token, mock_request):
    """Test get_token_and_project utility function, bad token"""
    response = su.get_token_and_project(mock_request)
    assert response == {"response": "MOCK_RESPONSE"}
    mock_get_token.assert_called_once()


@pytest.mark.hermetic
@patch.object(
    get_token, "get_token", return_value={"access_token": "MOCK_ACCESS_TOKEN"}
)
def test_get_token_and_project_bad_project_id(mock_get_token, mock_request):
    """Test get_token_and_project utility function, bad token"""
    response = su.get_token_and_project(mock_request)
    assert_response(response, 200, {"status": "BLOCKED", "reason": "NO_PROJECT_ID"})
    mock_get_token.assert_called_once()


@pytest.mark.hermetic
@patch.object(
    get_token, "get_token", return_value={"access_token": "MOCK_ACCESS_TOKEN"}
)
def test_get_token_and_project_success(mock_get_token, mock_request):
    """Test get_token_and_project utility function, bad token"""
    mock_request.args = {"project_id": "MOCK_PROJECT_ID"}
    response = su.get_token_and_project(mock_request)
    assert response == {"token": "MOCK_ACCESS_TOKEN", "project_id": "MOCK_PROJECT_ID"}
    mock_get_token.assert_called_once()


@pytest.mark.hermetic
@patch.object(su, "get_token_and_project", return_value={"response": "MOCK_RESPONSE"})
def test_get_restricted_service_status_bad_token(mock_get_token_project, mock_request):
    """Test get_restricted_service_status helper function, bad token/project"""
    response = su.get_restricted_service_status(mock_request, "MOCK_SERVICE_KEY")
    assert response == "MOCK_RESPONSE"
    mock_get_token_project.assert_called_once()


@pytest.mark.hermetic
@patch.object(
    su,
    "get_token_and_project",
    return_value={"token": "MOCK_ACCESS_TOKEN", "project_id": "MOCK_PROJECT_ID"},
)
@patch.object(su, "get_access_policy_name", return_value={"response": "MOCK_RESPONSE"})
def test_get_restricted_service_status_bad_policy(
    mock_get_access_policy, mock_get_token_project, mock_request
):
    """Test get_restricted_service_status helper function, bad policy"""
    response = su.get_restricted_service_status(mock_request, "MOCK_SERVICE_KEY")
    assert response == "MOCK_RESPONSE"
    mock_get_token_project.assert_called_once()
    mock_get_access_policy.assert_called_once()


@pytest.mark.hermetic
@patch.object(
    su,
    "get_token_and_project",
    return_value={"token": "MOCK_ACCESS_TOKEN", "project_id": "MOCK_PROJECT_ID"},
)
@patch.object(
    su,
    "get_access_policy_name",
    return_value={"access_policy_name": "/MOCK_ACCESS_POLICY_NAME"},
)
@patch.object(
    su,
    "get_restricted_services_status",
    return_value={"response": "MOCK_RESPONSE"},
)
def test_get_restricted_service_status_bad_status(
    mock_get_restricted_services_status,
    mock_get_access_policy,
    mock_get_token_project,
    mock_request,
):
    """Test get_restricted_service_status helper function, bad status"""
    response = su.get_restricted_service_status(mock_request, "MOCK_SERVICE_KEY")
    assert response == "MOCK_RESPONSE"
    mock_get_restricted_services_status.assert_called_once()
    mock_get_access_policy.assert_called_once()
    mock_get_token_project.assert_called_once()


@pytest.mark.hermetic
@patch.object(
    su,
    "get_token_and_project",
    return_value={"token": "MOCK_ACCESS_TOKEN", "project_id": "MOCK_PROJECT_ID"},
)
@patch.object(
    su,
    "get_access_policy_name",
    return_value={"access_policy_name": "/MOCK_ACCESS_POLICY_NAME"},
)
@patch.object(
    su,
    "get_restricted_services_status",
    return_value={"MOCK_SERVICE_KEY": "MOCK_SERVICE_STATUS"},
)
def test_get_restricted_service_status_success(
    mock_get_restricted_services_status,
    mock_get_access_policy,
    mock_get_token_project,
    mock_request,
):
    """Test get_restricted_service_status helper function, bad status"""
    response = su.get_restricted_service_status(mock_request, "MOCK_SERVICE_KEY")
    assert_response({"response": response}, 200, {"status": "MOCK_SERVICE_STATUS"})
    mock_get_restricted_services_status.assert_called_once()
    mock_get_access_policy.assert_called_once()
    mock_get_token_project.assert_called_once()
