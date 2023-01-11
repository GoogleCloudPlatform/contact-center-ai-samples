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


"""Blueprint for launchpad services."""

import json
import logging

import flask
import get_token
import requests

launchpad = flask.Blueprint("launchpad", __name__)
logger = logging.getLogger(__name__)


@launchpad.route("/get_principal", methods=["GET"])
def get_principal():
    """Get the email of the current principal for the session."""
    token_dict = get_token.get_token(flask.request, token_type="email")
    if "response" in token_dict:
        return flask.Response(status=200, response=json.dumps({"principal": None}))
    return flask.Response(
        status=200, response=json.dumps({"principal": token_dict["email"]})
    )


@launchpad.route("/validate_project_id", methods=["GET"])
def validate_project_id():
    """Confirm if the current project_id is valid for current user."""
    project_id = flask.request.args.get("project_id", None)
    logger.info("project_id to validate: %s", project_id)
    if not project_id:
        logger.info("project_id empty")
        return flask.Response(
            status=200, response=json.dumps({"status": False}, indent=2)
        )
    token_dict = get_token.get_token(flask.request, token_type="access_token")
    if "response" in token_dict:
        logger.info("ERROR TO DEBUG: %s", token_dict["response"])
        return token_dict["response"]
    access_token = token_dict["access_token"]

    headers = {}
    headers["Authorization"] = f"Bearer {access_token}"
    req = requests.get(
        f"https://cloudresourcemanager.googleapis.com/v1/projects/{project_id}",
        headers=headers,
        timeout=10,
    )

    if req.status_code == 200:
        return flask.Response(
            status=200, response=json.dumps({"status": True}, indent=2)
        )
    logger.info("cloudresourcemanager request not 200: %s", req.text)
    return flask.Response(status=200, response=json.dumps({"status": False}, indent=2))
