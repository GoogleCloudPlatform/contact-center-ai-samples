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

"""Utilities module for session blueprint."""

import os
from urllib.parse import urlparse

DEBUG_DOMAIN = "user-service.localhost"


def is_prod():
    """Indicator function, in production environment or not."""
    return os.getenv("PROD") == "true"


def user_service_domain(request):
    """Helper function to get host domain (dev and prod)."""
    if request.host_url in ["http://localhost:5001/", "http://localhost:8081/"]:
        assert not is_prod()
        domain = "user-service.localhost"
    else:
        assert is_prod()
        domain = urlparse(request.host_url).hostname
    return domain


def login_landing_uri(request, query_params=None):
    """Helper function to get landing location on host after login (dev and prod)."""
    if query_params is None:
        query_params = {}
    if request.host_url == "http://localhost:5001/":
        assert not is_prod()
        landing_uri = f"http://{DEBUG_DOMAIN}:3000"
    elif request.host_url == "http://localhost:8081/":
        assert not is_prod()
        landing_uri = f"http://{DEBUG_DOMAIN}:8080"
    else:
        assert is_prod()
        landing_uri = request.host_url.replace("http://", "https://")

    if landing_uri[-1] == "/":
        landing_uri = landing_uri[:-1]

    if query_params:
        param_string = "&".join([f"{key}={val}" for key, val in query_params.items()])
        landing_uri = f"{landing_uri}/?{param_string}"

    return landing_uri
