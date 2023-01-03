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

"""Module for testing analytics_blueprint.py"""

import analytics_utilities as au
import pytest
import session_utilities as su
from analytics_blueprint import analytics as blueprint
from conftest import MOCK_DOMAIN, generate_mock_register_action
from mock import patch


def get_result(
    app,
    endpoint,
):
    """Helper function to get result from a test client."""
    with app.test_client() as curr_client:
        return curr_client.post(
            endpoint,
            base_url=f"https://{MOCK_DOMAIN}",
        )


@pytest.mark.parametrize("app", [blueprint], indirect=["app"])
@pytest.mark.parametrize(
    "endpoint",
    [
        "/register_set_active_tutorial_tab",
        "/register_set_active_page",
    ],
)
@patch.object(au, "register_action", new_callable=generate_mock_register_action)
@patch.object(su, "user_service_domain", return_value=MOCK_DOMAIN)
def test_register_endpoints(
    mock_user_service_domain,
    mock_register_action,
    app,
    endpoint,
):
    """Test /register_set_active_page."""
    return_value = get_result(app, endpoint)
    mock_register_action.assert_called_once()
    mock_user_service_domain.assert_called_once()
    assert return_value.status_code == 200
