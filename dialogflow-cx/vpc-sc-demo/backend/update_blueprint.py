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

"""Module for updating configuration of assets."""

import base64
import json
import logging

import analytics_utilities as au
import flask
import requests
import status_utilities as su
import update_utilities as uu

DOMAIN = "webhook.internal"
update = flask.Blueprint("update", __name__)
logger = logging.getLogger(__name__)


@update.route("/update_webhook_access", methods=["POST"])
def update_webhook_access():  # pylint: disable=too-many-branches
    """Update webhook access to allow/disallow allUsers."""
    data = su.get_token_and_project(flask.request)
    if "response" in data:
        return data["response"]
    project_id, token = data["project_id"], data["token"]
    region = flask.request.args["region"]
    webhook_name = flask.request.args["webhook_name"]
    content = flask.request.get_json(silent=True)
    internal_only = content["status"]

    headers = {}
    headers["x-goog-user-project"] = project_id
    headers["Authorization"] = f"Bearer {token}"
    response = requests.get(
        (
            f"https://cloudfunctions.googleapis.com/v2/projects/{project_id}"
            f"/locations/{region}/functions/{webhook_name}:getIamPolicy"
        ),
        headers=headers,
        timeout=10,
    )
    if response.status_code != 200:
        logger.info(
            "  cloudfunctions API rejected getIamPolicy GET request: %s", response.text
        )
        return flask.Response(
            status=response.status_code, response=json.dumps({"error": response.text})
        )

    policy_dict = response.json()
    all_users_is_invoker_member = False
    for binding in policy_dict.get("bindings", []):
        for member in binding["members"]:
            if (
                member == "allUsers"
                and binding["role"] == "roles/cloudfunctions.invoker"
            ):
                all_users_is_invoker_member = True
    if (not internal_only and all_users_is_invoker_member) or (
        (internal_only) and (not all_users_is_invoker_member)
    ):
        # internal_only matches request; no change needed
        return flask.Response(status=200)

    if internal_only:
        for binding in policy_dict.get("bindings", []):
            for member in binding["members"]:
                if binding["role"] == "roles/cloudfunctions.invoker":
                    binding["members"] = [
                        member for member in binding["members"] if member != "allUsers"
                    ]
    else:
        if "bindings" not in policy_dict or len(policy_dict["bindings"]) == 0:
            policy_dict["bindings"] = [
                {"role": "roles/cloudfunctions.invoker", "members": []}
            ]
        invoker_role_exists = None
        for binding in policy_dict["bindings"]:
            if binding["role"] == "roles/cloudfunctions.invoker":
                invoker_role_exists = True
                binding["members"].append("allUsers")
        if not invoker_role_exists:
            policy_dict["bindings"].append(
                {"role": "roles/cloudfunctions.invoker", "members": ["allUsers"]}
            )
    response = requests.post(
        (
            f"https://cloudfunctions.googleapis.com/v1/projects/{project_id}"
            f"/locations/{region}/functions/{webhook_name}:setIamPolicy"
        ),
        headers=headers,
        json={"policy": policy_dict},
        timeout=10,
    )
    if response.status_code != 200:
        logger.info(
            "  cloudfunctions API rejected setIamPolicy POST request: %s", response.text
        )
        return flask.Response(
            status=response.status_code, response=json.dumps({"error": response.text})
        )
    response = flask.Response(status=200)
    return au.register_action(
        flask.request, response, au.ACTIONS.UPDATE_STATUS, {"service": "ingress"}
    )


@update.route("/update_webhook_ingress", methods=["POST"])
def update_webhook_ingress():
    """Update webhook ingress to allow/disallow external connections."""
    data = su.get_token_and_project(flask.request)
    if "response" in data:
        return data["response"]
    project_id, token = data["project_id"], data["token"]
    region = flask.request.args["region"]
    webhook_name = flask.request.args["webhook_name"]
    content = flask.request.get_json(silent=True)

    headers = {}
    headers["Content-type"] = "application/json"
    headers["x-goog-user-project"] = project_id
    headers["Authorization"] = f"Bearer {token}"
    response = requests.get(
        (
            f"https://cloudfunctions.googleapis.com/v1/projects/{project_id}"
            f"/locations/{region}/functions/{webhook_name}"
        ),
        headers=headers,
        timeout=10,
    )
    if response.status_code != 200:
        logger.info("  cloudfunctions API rejected GET request: %s", response.text)
        return flask.Response(
            status=response.status_code, response=json.dumps({"error": response.text})
        )

    webhook_data = response.json()
    ingress_settings = "ALLOW_INTERNAL_ONLY" if content["status"] else "ALLOW_ALL"
    if webhook_data["ingressSettings"] == ingress_settings:
        return flask.Response(status=200)

    webhook_data["ingressSettings"] = ingress_settings
    response = requests.patch(
        (
            f"https://cloudfunctions.googleapis.com/v1/projects/{project_id}"
            f"/locations/{region}/functions/{webhook_name}"
        ),
        headers=headers,
        json=webhook_data,
        timeout=10,
    )
    if response.status_code != 200:
        logger.info("  cloudfunctions API rejected PATCH request: %s", response.text)
        return flask.Response(
            status=response.status_code, response=json.dumps({"error": response.text})
        )
    response = flask.Response(status=200)
    return au.register_action(
        flask.request, response, au.ACTIONS.UPDATE_STATUS, {"service": "ingress"}
    )


@update.route("/update_security_perimeter_cloudfunctions", methods=["POST"])
def update_security_perimeter_cloudfunctions():
    """Update security perimeter, cloudfunctions."""
    response = uu.update_security_perimeter(
        flask.request, "cloudfunctions.googleapis.com"
    )
    return au.register_action(
        flask.request, response, au.ACTIONS.UPDATE_STATUS, {"service": "ingress"}
    )


@update.route("/update_security_perimeter_dialogflow", methods=["POST"])
def update_security_perimeter_dialogflow():
    """Update security perimeter, dialogflow."""
    response = uu.update_security_perimeter(flask.request, "dialogflow.googleapis.com")
    return au.register_action(
        flask.request, response, au.ACTIONS.UPDATE_STATUS, {"service": "ingress"}
    )


@update.route("/update_service_directory_webhook_fulfillment", methods=["POST"])
def update_service_directory_webhook_fulfillment():  # pylint: disable=too-many-return-statements,too-many-locals
    """Update agent webhook; toggle between service directory and generic webhook."""
    data = su.get_token_and_project(flask.request)
    if "response" in data:
        return data["response"]
    project_id, token = data["project_id"], data["token"]
    untrusted_region = flask.request.args["region"]
    if untrusted_region in ["us-central1"]:
        region = untrusted_region
    else:
        return flask.Response(
            status=200,
            response=json.dumps({"status": "BLOCKED", "reason": "UNKNOWN_REGION"}),
        )

    content = flask.request.get_json(silent=True)
    if content["status"] is True:
        fulfillment = "service-directory"
    else:
        fulfillment = "generic-web-service"

    bucket = flask.request.args["bucket"]
    webhook_name = flask.request.args["webhook_name"]
    webhook_trigger_uri = (
        f"https://{region}-{project_id}.cloudfunctions.net/{webhook_name}"
    )
    result = su.get_agents(token, project_id, region)
    if "response" in result:
        return result["response"]
    agent_name = result["data"]["Telecommunications"]["name"]
    result = su.get_webhooks(token, agent_name, project_id, region)
    if "response" in result:
        return result["response"]
    webhook_dict = result["data"]["cxPrebuiltAgentsTelecom"]
    webhook_name = webhook_dict["name"]
    if fulfillment == "generic-web-service":
        data = {
            "displayName": "cxPrebuiltAgentsTelecom",
            "genericWebService": {"uri": webhook_trigger_uri},
        }
    elif fulfillment == "service-directory":

        def encode(msg_bytes):
            return base64.b64encode(msg_bytes).decode("ascii")

        data = {
            "displayName": "cxPrebuiltAgentsTelecom",
            "serviceDirectory": {
                "service": (
                    f"projects/{project_id}/locations/{region}/"
                    f"namespaces/df-namespace"
                    f"/services/df-service"
                ),
                "genericWebService": {
                    "uri": f"https://{DOMAIN}",
                    "allowedCaCerts": [encode(uu.get_cert(token, project_id, bucket))],
                },
            },
        }
    else:
        return flask.Response(  # pragma: no cover
            status=500, response=f"Unexpected setting for fulfillment: {fulfillment}"
        )

    headers = {}
    headers["x-goog-user-project"] = project_id
    headers["Authorization"] = f"Bearer {token}"
    response = requests.patch(
        f"https://{region}-dialogflow.googleapis.com/v3/{webhook_name}",
        headers=headers,
        json=data,
        timeout=10,
    )
    if response.status_code != 200:
        logger.info(
            "  dialogflow API unexpectedly rejected invocation PATCH request: %s",
            response.text,
        )
        return flask.Response(
            status=response.status_code, response=json.dumps({"error": response.text})
        )
    response = flask.Response(status=200)
    return au.register_action(
        flask.request, response, au.ACTIONS.UPDATE_STATUS, {"service": "ingress"}
    )
