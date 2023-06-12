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

"""Module for testing asset_blueprint.py."""

import json

import analytics_utilities as au
import asset_utilities as asu
import get_token
import pytest
from asset_blueprint import ACCESS_POLICY_RESOURCE
from asset_blueprint import asset as blueprint
from conftest import MOCK_DOMAIN
from conftest import assert_response_ep as assert_response
from conftest import generate_mock_register_action
from mock import patch


def get_result(
    app,
    endpoint,
    method="get",
    json_data=None,
    query_dict=None,
):
    """Helper function to get result from a test client."""
    if query_dict is None:
        query_dict = {
            "project_id": "MOCK_PROJECT_ID",
            "region": "MOCK_REGION",
            "bucket": "MOCK_BUCKET_NAME",
        }

    with app.test_client() as curr_client:
        fcn = curr_client.get if method == "get" else curr_client.post
        kwargs = {
            "query_string": query_dict,
        }
        if json_data:
            kwargs["json"] = json_data
        return fcn(
            endpoint,
            base_url=f"https://{MOCK_DOMAIN}",
            **kwargs,
        )


@pytest.mark.parametrize(
    "app,endpoint,how",
    [
        (blueprint, "/asset_status", "get"),
        (blueprint, "/update_target", "post"),
    ],
    indirect=["app"],
)
@patch.object(
    get_token, "get_token", return_value={"access_token": "MOCK_ACCESS_TOKEN"}
)
@patch.object(asu, "validate_project_id", return_value="MOCK_RESPONSE")
def test_asset_status_bad_project_id(
    mock_get_token,
    mock_validate_project_id,
    app,
    endpoint,
    how,
):
    """Test endpoints, bad project_id provided."""
    return_value = get_result(
        app,
        endpoint,
        method=how,
        json_data={},
    )
    mock_get_token.assert_called_once()
    mock_validate_project_id.assert_called_once()
    assert_response(
        return_value,
        200,
        endpoint,
        "MOCK_RESPONSE",
    )


@pytest.mark.parametrize(
    "app,endpoint,how",
    [
        (blueprint, "/asset_status", "get"),
        (blueprint, "/update_target", "post"),
    ],
    indirect=["app"],
)
def test_asset_status_bad_token(app, endpoint, how):
    """Test asset endpoints, bad token"""
    with patch.object(
        get_token, "get_token", return_value={"response": "MOCK_RESPONSE"}
    ):
        with app.test_client() as curr_client:
            if how == "get":
                return_value = curr_client.get(
                    endpoint, base_url=f"https://{MOCK_DOMAIN}"
                )
            else:
                return_value = curr_client.post(
                    endpoint, base_url=f"https://{MOCK_DOMAIN}"
                )
    assert_response(return_value, 200, endpoint, "MOCK_RESPONSE")


@pytest.mark.parametrize(
    "app,endpoint,how",
    [
        (blueprint, "/asset_status", "get"),
        (blueprint, "/update_target", "post"),
    ],
    indirect=["app"],
)
@patch.object(
    get_token, "get_token", return_value={"access_token": "MOCK_ACCESS_TOKEN"}
)
def test_asset_status_no_project_id(mock_get_token, app, endpoint, how):
    """Test asset endpoints, no project_id"""
    return_value = get_result(
        app,
        endpoint,
        method=how,
        json_data={},
        query_dict={},
    )
    assert_response(
        return_value,
        200,
        endpoint,
        json.dumps({"status": "BLOCKED", "reason": "NO_PROJECT_ID"}),
    )
    mock_get_token.assert_called_once()


@pytest.mark.parametrize(
    "app,endpoint",
    [
        (blueprint, "/update_target"),
        (blueprint, "/asset_status"),
    ],
    indirect=["app"],
)
@patch.object(
    get_token, "get_token", return_value={"access_token": "MOCK_ACCESS_TOKEN"}
)
@patch.object(asu, "validate_project_id", return_value=None)
@patch.object(asu, "get_terraform_env", return_value={"response": "MOCK_RESPONSE"})
def test_asset_status_bad_terraform_env(
    mock_get_terraform_env,
    mock_validate_project_id,
    mock_get_token,
    app,
    endpoint,
):
    """Test /asset_status, bad response from get_terraform_env."""
    method = "post" if endpoint == "/update_target" else "get"
    return_value = get_result(
        app,
        endpoint,
        method=method,
        json_data={},
    )
    assert_response(return_value, 200, endpoint, "MOCK_RESPONSE")
    mock_get_token.assert_called_once()
    mock_get_terraform_env.assert_called_once()
    mock_validate_project_id.assert_called_once()


@pytest.mark.parametrize("app", [blueprint], indirect=["app"])
@patch.object(asu, "validate_project_id", return_value=None)
def test_asset_status_init_exit(validate_project_id, app):
    """Test /asset_status, init had nonzero return value."""
    endpoint = "/asset_status"
    with patch.object(
        get_token, "get_token", return_value={"access_token": "MOCK_ACCESS_TOKEN"}
    ):
        with patch.object(asu, "tf_init", return_value="MOCK_INIT"):
            return_value = get_result(app, endpoint)
    assert_response(return_value, 200, endpoint, "MOCK_INIT")
    validate_project_id.assert_called_once()


@pytest.mark.parametrize("app", [blueprint], indirect=["app"])
@patch.object(asu, "validate_project_id", return_value=None)
def test_asset_status_plan_exit(validate_project_id, app):
    """Test /asset_status, tf_plan has nonzero return"""
    endpoint = "/asset_status"
    with patch.object(
        get_token, "get_token", return_value={"access_token": "MOCK_ACCESS_TOKEN"}
    ):
        with patch.object(asu, "tf_init", return_value=None):
            with patch.object(
                asu, "tf_plan", return_value={"response": "MOCK_RESPONSE"}
            ):
                return_value = get_result(app, endpoint)
    assert_response(return_value, 200, endpoint, "MOCK_RESPONSE")
    validate_project_id.assert_called_once()


@pytest.mark.parametrize("app", [blueprint], indirect=["app"])
@patch.object(asu, "validate_project_id", return_value=None)
def test_asset_status_access_policy_err(mock_validate_project_id, app):
    """Test /asset_status, error in get_access_policy_title"""
    endpoint = "/asset_status"
    with patch.object(
        get_token, "get_token", return_value={"access_token": "MOCK_ACCESS_TOKEN"}
    ):
        with patch.object(asu, "tf_init", return_value=None):
            with patch.object(
                asu,
                "tf_plan",
                return_value={
                    "hooks": {
                        "refresh_complete": [
                            {
                                "resource": {"addr": ACCESS_POLICY_RESOURCE},
                                "id_value": "MOCK_ID_VALUE",
                            }
                        ]
                    }
                },
            ):
                with patch.object(
                    asu,
                    "get_access_policy_title",
                    return_value={"response": "MOCK_RESPONSE"},
                ):
                    return_value = get_result(app, endpoint)
    assert_response(return_value, 200, endpoint, "MOCK_RESPONSE")
    mock_validate_project_id.assert_called_once()


@pytest.mark.parametrize(
    "app, mock_policy,tf_state_list_err,expected",
    [
        (
            blueprint,
            False,
            False,
            json.dumps(
                {
                    "status": "OK",
                    "resources": "MOCK_RESOURCES",
                    "resource_id_dict": {"MOCK_ADDR": "MOCK_ID_VALUE"},
                    "accessPolicyTitle": None,
                }
            ),
        ),
        (blueprint, False, True, "MOCK_RESPONSE"),
        (
            blueprint,
            True,
            False,
            json.dumps(
                {
                    "status": "OK",
                    "resources": "MOCK_RESOURCES",
                    "resource_id_dict": {ACCESS_POLICY_RESOURCE: "MOCK_ID_VALUE"},
                    "accessPolicyTitle": "MOCK_ACCESS_POLICY_TITLE",
                }
            ),
        ),
        (blueprint, True, True, "MOCK_RESPONSE"),
    ],
    indirect=["app"],
)
@patch.object(asu, "tf_init", return_value=None)
@patch.object(au, "register_action", new_callable=generate_mock_register_action)
@patch.object(asu, "validate_project_id", return_value=None)
def test_asset_status(  # pylint: disable=too-many-arguments
    mock_validate_project_id,
    mock_register_action,
    mock_tf_init,
    app,
    mock_policy,
    tf_state_list_err,
    expected,
):
    """Test /asset_status"""
    if mock_policy:
        addr = ACCESS_POLICY_RESOURCE
        policy_return_value = {"access_policy_title": "MOCK_ACCESS_POLICY_TITLE"}
    else:
        addr = "MOCK_ADDR"
        policy_return_value = None
    if tf_state_list_err:
        state_list_return_value = {"response": "MOCK_RESPONSE"}
    else:
        state_list_return_value = {"resources": "MOCK_RESOURCES"}

    endpoint = "/asset_status"
    with patch.object(
        get_token, "get_token", return_value={"access_token": "MOCK_ACCESS_TOKEN"}
    ):
        with patch.object(
            asu,
            "tf_plan",
            return_value={
                "hooks": {
                    "refresh_complete": [
                        {
                            "resource": {"addr": addr},
                            "id_value": "MOCK_ID_VALUE",
                        }
                    ]
                }
            },
        ):
            with patch.object(
                asu, "get_access_policy_title", return_value=policy_return_value
            ):
                with patch.object(
                    asu, "tf_state_list", return_value=state_list_return_value
                ):
                    return_value = get_result(app, endpoint)
    assert_response(return_value, 200, endpoint, expected)
    mock_tf_init.assert_called_once()
    mock_validate_project_id.assert_called_once()
    if not tf_state_list_err:
        mock_register_action.assert_called_once()


@pytest.mark.parametrize(
    "app,json_data,call_count,apply_return_value,state",
    [
        (blueprint, {"destroy": False}, 1, None, {"response": "MOCK_RESPONSE"}),
        (
            blueprint,
            {"destroy": False, "targets": ["all"]},
            1,
            None,
            {"response": "MOCK_RESPONSE"},
        ),
        (
            blueprint,
            {"destroy": False, "targets": ["MOCK_TARGET"]},
            1,
            None,
            {"response": "MOCK_RESPONSE"},
        ),
        (
            blueprint,
            {"destroy": False, "targets": ["MOCK_TARGET_1", "MOCK_TARGET_2"]},
            2,
            "MOCK_APPLY_RETURN_VALUE",
            {"response": "MOCK_RESPONSE"},
        ),
        (
            blueprint,
            {"destroy": False, "targets": ["MOCK_TARGET_1", "MOCK_TARGET_2"]},
            2,
            None,
            {"response": "MOCK_RESPONSE"},
        ),
        (
            blueprint,
            {"destroy": False, "targets": ["MOCK_TARGET_1", "MOCK_TARGET_2"]},
            2,
            None,
            {"resources": ["MOCK_RESOURCE"]},
        ),
    ],
    indirect=["app"],
)
@patch.object(asu, "tf_init", return_value=None)
@patch.object(asu, "tf_plan", return_value=None)
@patch.object(
    get_token, "get_token", return_value={"access_token": "MOCK_ACCESS_TOKEN"}
)
@patch.object(au, "register_action", new_callable=generate_mock_register_action)
@patch.object(asu, "validate_project_id", return_value=None)
def test_update_target(  # pylint: disable=too-many-arguments
    mock_validate_project_id,
    mock_register_action,
    mock_get_token,
    mock_tf_plan,
    mock_tf_init,
    app,
    json_data,
    call_count,
    apply_return_value,
    state,
):
    """test /update_target,"""
    endpoint = "/update_target"
    with patch.object(
        asu, "tf_apply", return_value=apply_return_value
    ) as mock_tf_apply:
        with patch.object(asu, "tf_state_list", return_value=state):
            return_value = get_result(
                app,
                endpoint,
                method="post",
                json_data=json_data,
            )
    mock_get_token.assert_called_once()
    mock_tf_init.assert_called_once()
    mock_validate_project_id.assert_called_once()
    assert mock_tf_plan.call_count == call_count
    assert mock_tf_apply.call_count == call_count
    if apply_return_value:
        assert_response(return_value, 200, endpoint, "MOCK_APPLY_RETURN_VALUE")
    elif "response" in state:
        assert_response(return_value, 200, endpoint, "MOCK_RESPONSE")
    else:
        assert_response(
            return_value,
            200,
            endpoint,
            json.dumps({"status": "OK", "resources": ["MOCK_RESOURCE"]}),
        )
        mock_register_action.assert_called_once()


@patch.object(
    get_token, "get_token", return_value={"access_token": "MOCK_ACCESS_TOKEN"}
)
@patch.object(asu, "tf_init", return_value="MOCK_RESPONSE")
@pytest.mark.parametrize("app", [blueprint], indirect=["app"])
@patch.object(asu, "validate_project_id", return_value=None)
def test_update_target_bad_init(
    mock_validate_project_id,
    mock_tf_init,
    mock_get_token,
    app,
):
    """test /update_target, tf_init has non-zero return value."""
    endpoint = "/update_target"
    return_value = get_result(
        app,
        endpoint,
        method="post",
        json_data={"destroy": False},
    )
    mock_get_token.assert_called_once()
    mock_tf_init.assert_called_once()
    mock_validate_project_id.assert_called_once()
    assert_response(return_value, 200, endpoint, "MOCK_RESPONSE")


@patch.object(
    get_token, "get_token", return_value={"access_token": "MOCK_ACCESS_TOKEN"}
)
@patch.object(asu, "tf_init", return_value=None)
@patch.object(asu, "tf_plan", return_value={"response": "MOCK_RESPONSE"})
@pytest.mark.parametrize("app", [blueprint], indirect=["app"])
@patch.object(asu, "validate_project_id", return_value=None)
def test_update_target_bad_plan(
    mock_validate_project_id,
    mock_tf_plan,
    mock_tf_init,
    mock_get_token,
    app,
):
    """test /update_target, tf_plan has non-zero return value."""
    endpoint = "/update_target"
    return_value = get_result(
        app,
        endpoint,
        method="post",
        json_data={"destroy": False, "targets": ["MOCK_TARGET"]},
    )
    mock_tf_plan.assert_called_once()
    mock_get_token.assert_called_once()
    mock_tf_init.assert_called_once()
    mock_validate_project_id.assert_called_once()
    assert_response(return_value, 200, endpoint, "MOCK_RESPONSE")
