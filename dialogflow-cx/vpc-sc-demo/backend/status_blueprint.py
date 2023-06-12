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

"""Blueprint for checking project status."""

import json
import logging

import flask
import requests
import status_utilities as su

status = flask.Blueprint("status", __name__)
logger = logging.getLogger(__name__)


@status.route("/restricted_services_status_cloudfunctions", methods=["GET"])
def restricted_services_status_cloudfunctions():
    """Get boolean status of wether cloudfunctions is restricted."""
    return su.get_restricted_service_status(flask.request, "cloudfunctions_restricted")


@status.route("/restricted_services_status_dialogflow", methods=["GET"])
def restricted_services_status_dialogflow():
    """Get boolean status of wether dialogflow is restricted."""
    return su.get_restricted_service_status(flask.request, "dialogflow_restricted")


@status.route("/webhook_ingress_internal_only_status", methods=["GET"])
def webhook_ingress_internal_only_status():
    """Get boolean status of internally restricted webhook ingress."""
    data = su.get_token_and_project(flask.request)
    if "response" in data:
        return data["response"]
    project_id, token = data["project_id"], data["token"]
    region = flask.request.args["region"]
    webhook_name = flask.request.args["webhook_name"]

    response = su.check_function_exists(token, project_id, region, webhook_name)
    if "response" in response:
        return response["response"]

    headers = {}
    headers["x-goog-user-project"] = project_id
    headers["Authorization"] = f"Bearer {token}"
    result = requests.get(
        (
            "https://cloudfunctions.googleapis.com/v1/projects/"
            f"{project_id}/locations/{region}/functions/{webhook_name}"
        ),
        headers=headers,
        timeout=10,
    )
    if result.status_code != 200:
        logger.info("  cloudfunctions API rejected request: %s", result.text)
        return flask.abort(result.status_code)
    result_dict = result.json()
    if result_dict["ingressSettings"] in [
        "ALLOW_INTERNAL_ONLY",
        "ALLOW_INTERNAL_AND_GCLB",
    ]:
        return flask.Response(status=200, response=json.dumps({"status": True}))
    return flask.Response(status=200, response=json.dumps({"status": False}))


@status.route("/webhook_access_allow_unauthenticated_status", methods=["GET"])
def webhook_access_allow_unauthenticated_status():  # pylint: disable=too-many-branches,too-many-return-statements
    """Get boolean status of allow unauthenticated webhook access."""
    data = su.get_token_and_project(flask.request)
    if "response" in data:
        return data["response"]
    project_id, token = data["project_id"], data["token"]
    region = flask.request.args["region"]
    webhook_name = flask.request.args["webhook_name"]

    response = su.check_function_exists(token, project_id, region, webhook_name)
    if "response" in response:
        return response["response"]

    headers = {}
    headers["x-goog-user-project"] = project_id
    headers["Authorization"] = f"Bearer {token}"
    result = requests.get(
        (
            "https://cloudfunctions.googleapis.com/v2/"
            f"projects/{project_id}/locations/{region}/"
            f"functions/{webhook_name}:getIamPolicy"
        ),
        headers=headers,
        timeout=10,
    )
    if result.status_code == 403:
        if (result.json()["error"]["status"] == "PERMISSION_DENIED") and (
            result.json()["error"]["message"].startswith(
                "Permission 'cloudfunctions.functions.getIamPolicy' denied"
            )
        ):
            return flask.Response(
                status=200,
                response=json.dumps(
                    {"status": "BLOCKED", "reason": "PERMISSION_DENIED"}
                ),
            )
        if (result.json()["error"]["status"] == "PERMISSION_DENIED") and (
            result.json()["error"]["message"].startswith(
                "Cloud Functions API has not been used in project"
            )
        ):
            return flask.Response(
                status=200,
                response=json.dumps(
                    {"status": "BLOCKED", "reason": "CLOUDFUNCTIONS_API_DISABLED"}
                ),
            )
        for details in result.json()["error"]["details"]:
            for violation in details["violations"]:
                if violation["type"] == "VPC_SERVICE_CONTROLS":
                    return flask.Response(
                        status=200,
                        response=json.dumps(
                            {"status": "BLOCKED", "reason": "VPC_SERVICE_CONTROLS"}
                        ),
                    )
        return flask.Response(status=500, response=result.text)
    if result.status_code != 200:
        logger.info("  cloudfunctions API rejected request: %s", result.text)
        return flask.abort(result.status_code)
    policy_dict = result.json()
    all_users_is_invoker_member = False
    for binding in policy_dict.get("bindings", []):
        for member in binding.get("members", []):
            if (
                member == "allUsers"
                and binding["role"] == "roles/cloudfunctions.invoker"
            ):
                all_users_is_invoker_member = True

    logger.info("  all_users_is_invoker_member: %s", all_users_is_invoker_member)
    if all_users_is_invoker_member:
        return flask.Response(status=200, response=json.dumps({"status": False}))
    return flask.Response(status=200, response=json.dumps({"status": True}))


@status.route("/service_directory_webhook_fulfillment_status", methods=["GET"])
def service_directory_webhook_fulfillment_status():
    """Get boolean status of service directory usage in webhook."""
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

    result = su.get_agents(token, project_id, region)
    if "response" in result:
        return result["response"]
    if "Telecommunications" not in result["data"]:
        return flask.Response(
            status=200,
            response=json.dumps({"status": "BLOCKED", "reason": "AGENT_NOT_FOUND"}),
        )
    agent_name = result["data"]["Telecommunications"]["name"]
    result = su.get_webhooks(token, agent_name, project_id, region)
    if "response" in result:
        response = result["response"]
    else:
        webhook_dict = result["data"]["cxPrebuiltAgentsTelecom"]
        if "serviceDirectory" in webhook_dict:
            response = flask.Response(status=200, response=json.dumps({"status": True}))
        else:
            response = flask.Response(
                status=200, response=json.dumps({"status": False})
            )
    return response
