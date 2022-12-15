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


"""Blueprint for serving session and logout frontend."""

import json
import logging
import os
import uuid
from base64 import b64encode
from urllib.parse import urlparse

import flask

logger = logging.getLogger(__name__)
session = flask.Blueprint("session", __name__)

AUTH_SERVICE_HOSTNAME = "auth.dialogflow-demo.app"
AUTH_SERVICE_LOGIN_ENDPOINT = f"http://{AUTH_SERVICE_HOSTNAME}/login"
PUBLIC_PEM_FILENAME = "public_key.pem"
DEBUG_DOMAIN = "user-service.localhost"


def user_service_domain(request):
    """Helper function to get host domain (dev and prod)."""
    prod = os.getenv("PROD") == "true"
    if request.host_url in ["http://localhost:5001/", "http://localhost:8081/"]:
        assert not prod
        domain = "user-service.localhost"
    else:
        assert prod
        domain = urlparse(request.host_url).hostname
    return domain


def login_landing_uri(request, query_params=None):
    """Helper function to get landing location on host after login (dev and prod)."""
    if query_params is None:
        query_params = {}
    prod = os.getenv("PROD") == "true"
    if request.host_url == "http://localhost:5001/":
        assert not prod
        landing_uri = f"http://{DEBUG_DOMAIN}:3000"
    elif request.host_url == "http://localhost:8081/":
        assert not prod
        landing_uri = f"http://{DEBUG_DOMAIN}:8080"
    else:
        assert prod
        landing_uri = request.host_url.replace("http://", "https://")

    if landing_uri[-1] == "/":
        landing_uri = landing_uri[:-1]

    if query_params:
        param_string = "&".join([f"{key}={val}" for key, val in query_params.items()])
        landing_uri = f"{landing_uri}/?{param_string}"

    return landing_uri


@session.route("/session", methods=["GET"])
def session_route():
    """Get session cookie."""
    session_id = uuid.uuid4().hex
    with open(PUBLIC_PEM_FILENAME, "r", encoding="utf8") as file_handle:
        public_pem = file_handle.read()
    state = b64encode(
        json.dumps(
            {
                "return_to": login_landing_uri(
                    flask.request, query_params=flask.request.args
                ),
                "session_id": session_id,
                "public_pem": public_pem,
            }
        ).encode()
    ).decode()
    response = flask.redirect(f"{AUTH_SERVICE_LOGIN_ENDPOINT}?state={state}")
    response.set_cookie(
        "session_id",
        value=session_id,
        secure=True,
        httponly=True,
        domain=user_service_domain(flask.request),
    )
    response.set_cookie(
        "user_logged_in",
        value="true",
        secure=True,
        httponly=False,
        domain=user_service_domain(flask.request),
    )
    return response


@session.route("/logout", methods=["GET"])
def logout():
    """Remove session cookie."""
    response = flask.redirect(
        login_landing_uri(flask.request, query_params=flask.request.args)
    )
    response.delete_cookie("session_id", domain=user_service_domain(flask.request))
    response.delete_cookie("user_logged_in", domain=user_service_domain(flask.request))
    return response
