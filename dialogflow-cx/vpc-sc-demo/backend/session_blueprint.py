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

import datetime
import json
import logging
import uuid
from base64 import b64encode

import flask
import session_utilities as su

logger = logging.getLogger(__name__)
session = flask.Blueprint("session", __name__)

AUTH_SERVICE_HOSTNAME = "auth.dialogflow-demo.app"
AUTH_SERVICE_LOGIN_ENDPOINT = f"http://{AUTH_SERVICE_HOSTNAME}/login"
PUBLIC_PEM_FILENAME = "public_key.pem"
DEBUG_DOMAIN = "user-service.localhost"


@session.route("/session", methods=["GET"])
def session_route():
    """Get session cookie."""
    session_id = uuid.uuid4().hex
    with open(PUBLIC_PEM_FILENAME, "r", encoding="utf8") as file_handle:
        public_pem = file_handle.read()
    state = b64encode(
        json.dumps(
            {
                "return_to": su.login_landing_uri(
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
        domain=su.user_service_domain(flask.request),
        expires=datetime.datetime.now() + datetime.timedelta(hours=1),
    )
    response.set_cookie(
        "user_logged_in",
        value="true",
        secure=True,
        httponly=False,
        domain=su.user_service_domain(flask.request),
        expires=datetime.datetime.now() + datetime.timedelta(hours=1),
    )
    return response


@session.route("/logout", methods=["GET"])
def logout():
    """Remove session cookie."""
    response = flask.redirect(
        su.login_landing_uri(flask.request, query_params=flask.request.args)
    )
    response.delete_cookie("session_id", domain=su.user_service_domain(flask.request))
    response.delete_cookie(
        "user_logged_in", domain=su.user_service_domain(flask.request)
    )
    return response
