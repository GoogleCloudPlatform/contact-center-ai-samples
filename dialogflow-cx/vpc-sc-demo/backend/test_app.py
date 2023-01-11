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

"""Unit tests for app.py."""

import app
import pytest


def get_url_map(curr_app):
    """Get a map of all endpoints."""
    return {str(rule): rule for rule in curr_app.url_map.iter_rules()}


@pytest.mark.hermetic
@pytest.mark.parametrize(
    "route",
    [
        "/static/<path:filename>",
        "/build/<path:filename>",
        "/",
        "/<path:path>",
    ],
)
def test_root_routes(route):
    """Assert frontend endpoints are configured for GET."""
    url_map = get_url_map(app.app)
    assert "GET" in url_map[route].methods
