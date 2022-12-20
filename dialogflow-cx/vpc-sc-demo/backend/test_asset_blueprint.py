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

import asset_utilities as au
import flask
import get_token
import pytest
from asset_blueprint import ACCESS_POLICY_RESOURCE
from asset_blueprint import asset as blueprint
from conftest import MOCK_DOMAIN
from conftest import assert_response_ep as assert_response
from mock import patch


@pytest.fixture
def app():
    """Fixture for tests on session blueprint."""
    curr_app = flask.Flask(__name__)
    curr_app.register_blueprint(blueprint)
    curr_app.config["TESTING"] = True
    return curr_app


def get_result(
    curr_app,
    endpoint,
    method='get',
    json_data=None,
):
    """Helper function to get result from a test client."""
    with curr_app.test_client() as curr_client:
        fcn = curr_client.get if method == 'get' else curr_client.post
        kwargs = {
            'query_string': {
                "project_id": "MOCK_PROJECT_ID",
                "region": "MOCK_REGION",
                "bucket": "MOCK_BUCKET_NAME",
            },
        }
        if json_data:
            kwargs['json']=json_data
        return fcn(
            endpoint,
            base_url=f"https://{MOCK_DOMAIN}",
            **kwargs,
        )


@pytest.mark.parametrize(
    "endpoint,how",
    [
        ("/asset_status", "get"),
        ("/update_target", "post"),
    ],
)
def test_asset_status_bad_token(
    app, endpoint, how
):  # pylint: disable=redefined-outer-name
    """Test /asset_status, bad token"""
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


def test_asset_status_init_exit(app):  # pylint: disable=redefined-outer-name
    """Test /asset_status, init had nonzero return value."""
    endpoint = "/asset_status"
    with patch.object(
        get_token, "get_token", return_value={"access_token": "MOCK_ACCESS_TOKEN"}
    ):
        with patch.object(au, "tf_init", return_value="MOCK_INIT"):
            return_value = get_result(app, endpoint)
    assert_response(return_value, 200, endpoint, "MOCK_INIT")


def test_asset_status_plan_exit(app):  # pylint: disable=redefined-outer-name
    """Test /asset_status, tf_plan has nonzero return"""
    endpoint = "/asset_status"
    with patch.object(
        get_token, "get_token", return_value={"access_token": "MOCK_ACCESS_TOKEN"}
    ):
        with patch.object(au, "tf_init", return_value=None):
            with patch.object(
                au, "tf_plan", return_value={"response": "MOCK_RESPONSE"}
            ):
                return_value = get_result(app, endpoint)
    assert_response(return_value, 200, endpoint, "MOCK_RESPONSE")


def test_asset_status_access_policy_err(app):  # pylint: disable=redefined-outer-name
    """Test /asset_status, error in get_access_policy_title"""
    endpoint = "/asset_status"
    with patch.object(
        get_token, "get_token", return_value={"access_token": "MOCK_ACCESS_TOKEN"}
    ):
        with patch.object(au, "tf_init", return_value=None):
            with patch.object(
                au,
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
                    au,
                    "get_access_policy_title",
                    return_value={"response": "MOCK_RESPONSE"},
                ):
                    return_value = get_result(app, endpoint)
    assert_response(return_value, 200, endpoint, "MOCK_RESPONSE")


@pytest.mark.parametrize(
    "mock_policy,tf_state_list_err,expected",
    [
        (
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
        (False, True, "MOCK_RESPONSE"),
        (
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
        (True, True, "MOCK_RESPONSE"),
    ],
)
@patch.object(au, "tf_init", return_value=None)
def test_asset_status(
    mock_tf_init,
    app,  # pylint: disable=redefined-outer-name
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
            au,
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
                au, "get_access_policy_title", return_value=policy_return_value
            ):
                with patch.object(
                    au, "tf_state_list", return_value=state_list_return_value
                ):
                    return_value = get_result(app, endpoint)
    assert_response(return_value, 200, endpoint, expected)
    mock_tf_init.assert_called_once()


@pytest.mark.parametrize(
    "json_data,call_count,apply_return_value,state",
    [
        ({"destroy": False}, 1, None, {"response": "MOCK_RESPONSE"}),
        (
            {"destroy": False, "targets": ["all"]},
            1,
            None,
            {"response": "MOCK_RESPONSE"},
        ),
        (
            {"destroy": False, "targets": ["MOCK_TARGET"]},
            1,
            None,
            {"response": "MOCK_RESPONSE"},
        ),
        (
            {"destroy": False, "targets": ["MOCK_TARGET_1", "MOCK_TARGET_2"]},
            2,
            "MOCK_APPLY_RETURN_VALUE",
            {"response": "MOCK_RESPONSE"},
        ),
        (
            {"destroy": False, "targets": ["MOCK_TARGET_1", "MOCK_TARGET_2"]},
            2,
            None,
            {"response": "MOCK_RESPONSE"},
        ),
        (
            {"destroy": False, "targets": ["MOCK_TARGET_1", "MOCK_TARGET_2"]},
            2,
            None,
            {"resources": ["MOCK_RESOURCE"]},
        ),
    ],
)
@patch.object(au, "tf_init", return_value=None)
@patch.object(au, "tf_plan", return_value=None)
@patch.object(
    get_token, "get_token", return_value={"access_token": "MOCK_ACCESS_TOKEN"}
)
def test_update_target(  # pylint: disable=too-many-arguments
    mock_get_token,
    mock_tf_plan,
    mock_tf_init,
    app,  # pylint: disable=redefined-outer-name
    json_data,
    call_count,
    apply_return_value,
    state,
):
    """test /update_target,"""
    endpoint = "/update_target"
    with patch.object(au, "tf_apply", return_value=apply_return_value) as mock_tf_apply:
        with patch.object(au, "tf_state_list", return_value=state):
            return_value = get_result(
                app,
                endpoint,
                method='post',
                json_data=json_data,
            )
    mock_get_token.assert_called_once()
    mock_tf_init.assert_called_once()
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


@patch.object(
    get_token, "get_token", return_value={"access_token": "MOCK_ACCESS_TOKEN"}
)
@patch.object(au, "tf_init", return_value="MOCK_RESPONSE")
def test_update_target_bad_init(
    mock_tf_init,
    mock_get_token,
    app,  # pylint: disable=redefined-outer-name
):
    """test /update_target, tf_init has non-zero return value."""
    endpoint = "/update_target"
    return_value = get_result(
        app,
        endpoint,
        method='post',
        json_data={"destroy": False},
    )
    mock_get_token.assert_called_once()
    mock_tf_init.assert_called_once()
    assert_response(return_value, 200, endpoint, "MOCK_RESPONSE")


@patch.object(
    get_token, "get_token", return_value={"access_token": "MOCK_ACCESS_TOKEN"}
)
@patch.object(au, "tf_init", return_value=None)
@patch.object(au, "tf_plan", return_value={'response':'MOCK_RESPONSE'})
def test_update_target_bad_plan(
    mock_tf_plan,
    mock_tf_init,
    mock_get_token,
    app,  # pylint: disable=redefined-outer-name
):
    """test /update_target, tf_plan has non-zero return value."""
    endpoint = "/update_target"
    return_value = get_result(
        app,
        endpoint,
        method='post',
        json_data={"destroy": False, 'targets':['MOCK_TARGET']},
    )
    mock_tf_plan.assert_called_once()
    mock_get_token.assert_called_once()
    mock_tf_init.assert_called_once()
    assert_response(return_value, 200, endpoint, "MOCK_RESPONSE")
