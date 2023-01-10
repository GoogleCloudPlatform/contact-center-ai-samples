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

"""Utility Module to get status of project assets."""

import json
import logging

import flask
import get_token
import requests

logger = logging.getLogger(__name__)


def get_project_number(token, project_id):
    """Get project number using cloudresourcemanager API."""
    headers = {}
    headers["Content-type"] = "application/json"
    headers["Authorization"] = f"Bearer {token}"
    result = requests.get(
        f"https://cloudresourcemanager.googleapis.com/v1/projects/{project_id}",
        headers=headers,
        timeout=10,
    )
    if "projectNumber" in result.json():
        return {"project_number": result.json()["projectNumber"]}
    return {
        "response": flask.Response(
            status=200,
            response=json.dumps({"status": "BLOCKED", "reason": "NO_PROJECT"}),
        )
    }


def get_access_policy_name(token, access_policy_title, project_id, error_code=200):
    """Get access policy name using cloudresourcemanager API."""
    if not access_policy_title:
        return {
            "response": flask.Response(
                status=error_code,
                response=json.dumps(
                    {"status": "BLOCKED", "reason": "NO_ACCESS_POLICY"}
                ),
            )
        }

    headers = {}
    headers["Content-type"] = "application/json"
    headers["Authorization"] = f"Bearer {token}"
    response = requests.post(
        f"https://cloudresourcemanager.googleapis.com/v1/projects/{project_id}:getAncestry",
        headers=headers,
        timeout=10,
    )

    if response.status_code != 200:
        return {
            "response": flask.Response(
                status=error_code,
                response=json.dumps({"status": "BLOCKED", "reason": "UNKNOWN_STATUS"}),
            )
        }

    organization_id = None
    for ancestor_dict in response.json().get("ancestor", []):
        if ancestor_dict["resourceId"]["type"] == "organization":
            organization_id = ancestor_dict["resourceId"]["id"]
    if not organization_id:
        return {
            "response": flask.Response(
                status=error_code,
                response=json.dumps({"status": "BLOCKED", "reason": "NO_ORGANIZATION"}),
            )
        }

    response = get_project_number(token, project_id)
    if "response" in response:
        return response
    project_number = response["project_number"]

    headers = {}
    headers["Content-type"] = "application/json"
    headers["Authorization"] = f"Bearer {token}"
    response = requests.get(
        (
            "https://accesscontextmanager.googleapis.com/v1/"
            f"accessPolicies?parent=organizations/{organization_id}"
        ),
        headers=headers,
        timeout=10,
    )

    for policy in response.json().get("accessPolicies", []):
        if policy["title"] == access_policy_title:
            if f"projects/{project_number}" in policy["scopes"]:
                return {"access_policy_name": policy["name"]}

    return {
        "response": flask.Response(
            status=error_code,
            response=json.dumps({"status": "BLOCKED", "reason": "POLICY_NOT_FOUND"}),
        )
    }


def get_service_perimeter_data_uri(
    token,
    project_id,
    access_policy_name,
    perimeter_title="df_webhook",
):
    """Get uri for for service perimeter."""
    access_policy_id = access_policy_name.split("/")[1]
    headers = {}
    headers["x-goog-user-project"] = project_id
    headers["Authorization"] = f"Bearer {token}"
    response = requests.get(
        (
            f"https://accesscontextmanager.googleapis.com/v1/"
            f"accessPolicies/{access_policy_id}/servicePerimeters"
        ),
        headers=headers,
        timeout=10,
    )
    if response.status_code != 200:
        if (response.json()["error"]["status"] == "PERMISSION_DENIED") and (
            response.json()["error"]["message"].startswith(
                "Access Context Manager API has not been used in project"
            )
        ):
            response = flask.Response(
                status=200,
                response=json.dumps(
                    {
                        "status": "BLOCKED",
                        "reason": "ACCESS_CONTEXT_MANAGER_API_DISABLED",
                    }
                ),
            )
            return {"response": response}
        if response.json()["error"]["status"] == "PERMISSION_DENIED":
            response = flask.Response(
                status=200,
                response=json.dumps(
                    {"status": "BLOCKED", "reason": "PERMISSION_DENIED"}
                ),
            )
            return {"response": response}
        logger.info("  accesscontextmanager API rejected request: %s", response.text)
        return {"response": flask.Response(status=500, response=response.text)}

    for service_perimeter_dict in response.json().get("servicePerimeters", []):
        if service_perimeter_dict["title"] == perimeter_title:
            return {
                "uri": (
                    "https://accesscontextmanager.googleapis.com/v1/"
                    f'{service_perimeter_dict["name"]}'
                )
            }

    return {
        "response": flask.Response(
            status=200,
            response=json.dumps({"status": "BLOCKED", "reason": "PERIMETER_NOT_FOUND"}),
        )
    }


def get_service_perimeter_status(token, project_id, access_policy_name):
    """Get service perimeter status using accesscontextmanager API."""
    headers = {}
    headers["x-goog-user-project"] = project_id
    headers["Authorization"] = f"Bearer {token}"
    response = get_service_perimeter_data_uri(token, project_id, access_policy_name)
    if "response" in response:
        return response
    service_perimeter_data_uri = response["uri"]
    result = requests.get(service_perimeter_data_uri, headers=headers, timeout=10)
    if result.status_code != 200:
        logger.info("  accesscontextmanager API rejected request: %s", result.text)
        if (result.json()["error"]["status"] == "PERMISSION_DENIED") and (
            result.json()["error"]["message"].startswith(
                "Access Context Manager API has not been used in project"
            )
        ):
            # Potential bug: should return a dict?
            return flask.Response(
                status=200,
                response=json.dumps(
                    {
                        "status": "BLOCKED",
                        "reason": "ACCESS_CONTEXT_MANAGER_API_DISABLED",
                    }
                ),
            )
        if result.json()["error"]["status"] == "PERMISSION_DENIED":
            response = flask.Response(
                status=200,
                response=json.dumps(
                    {"status": "BLOCKED", "reason": "PERMISSION_DENIED"}
                ),
            )
            return {"response": response}
        response = flask.Response(status=result.status_code, response=result.text)
        return {"response": response}
    return result.json()


def get_restricted_services_status(token, project_id, access_policy_name):
    """Check which services are restricted using accesscontextmanager API."""
    service_perimeter_status = get_service_perimeter_status(
        token, project_id, access_policy_name
    )
    if "response" in service_perimeter_status:
        return service_perimeter_status
    status_dict = {}
    if "restrictedServices" not in service_perimeter_status["status"]:
        status_dict["cloudfunctions_restricted"] = False
        status_dict["dialogflow_restricted"] = False
    else:
        status_dict["cloudfunctions_restricted"] = (
            "cloudfunctions.googleapis.com"
            in service_perimeter_status["status"]["restrictedServices"]
        )
        status_dict["dialogflow_restricted"] = (
            "dialogflow.googleapis.com"
            in service_perimeter_status["status"]["restrictedServices"]
        )
    return status_dict


def check_function_exists(token, project_id, region, function_name):
    """Check if function exists using cloudfunctions api."""
    headers = {}
    headers["x-goog-user-project"] = project_id
    headers["Authorization"] = f"Bearer {token}"
    result = requests.get(
        (
            f"https://cloudfunctions.googleapis.com/v1/"
            f"projects/{project_id}/locations/{region}/functions/{function_name}"
        ),
        headers=headers,
        timeout=10,
    )
    if result.status_code == 200:
        response = {"status": "OK"}
    elif result.status_code == 404 and result.json()["error"]["status"] == "NOT_FOUND":
        response = {
            "response": flask.Response(
                status=200,
                response=json.dumps(
                    {"status": "BLOCKED", "reason": "WEBHOOK_NOT_FOUND"}
                ),
            )
        }
    elif result.status_code == 403 and result.json()["error"]["message"].startswith(
        "Cloud Functions API has not been used in project"
    ):
        response = {
            "response": flask.Response(
                status=200,
                response=json.dumps(
                    {"status": "BLOCKED", "reason": "CLOUDFUNCTIONS_API_DISABLED"}
                ),
            )
        }
    elif result.status_code == 403:
        if (result.json()["error"]["status"] == "PERMISSION_DENIED") and (
            result.json()["error"]["message"].startswith(
                "Permission 'cloudfunctions.functions.get' denied on resource"
            )
        ):
            response = {
                "response": flask.Response(
                    status=200,
                    response=json.dumps(
                        {"status": "BLOCKED", "reason": "PERMISSION_DENIED"}
                    ),
                )
            }
        else:
            response = None
            for details in result.json()["error"]["details"]:
                for violation in details["violations"]:
                    if violation["type"] == "VPC_SERVICE_CONTROLS":
                        response = {
                            "response": flask.Response(
                                status=200,
                                response=json.dumps(
                                    {
                                        "status": "BLOCKED",
                                        "reason": "VPC_SERVICE_CONTROLS",
                                    }
                                ),
                            )
                        }
            if response is None:
                response = {
                    "response": flask.Response(status=500, response=result.text)
                }
    else:
        response = {
            "response": flask.Response(status=500, response=json.dumps(result.json()))
        }
    return response


def get_agents(token, project_id, region):  # pylint: disable=too-many-branches
    """Get agents using dialogflow API"""
    headers = {}
    headers["x-goog-user-project"] = project_id
    headers["Authorization"] = f"Bearer {token}"
    if region not in ["us-central1"]:
        return {
            "response": flask.Response(
                status=200,
                response=json.dumps({"status": "BLOCKED", "reason": "UNKNOWN_REGION"}),
            )
        }
    result = requests.get(
        (
            f"https://{region}-dialogflow.googleapis.com/v3/"
            f"projects/{project_id}/locations/{region}/agents"
        ),
        headers=headers,
        timeout=10,
    )
    if result.status_code == 403:
        if (result.json()["error"]["status"] == "PERMISSION_DENIED") and (
            result.json()["error"]["message"].startswith(
                "Dialogflow API has not been used in project"
            )
        ):
            response = {
                "response": flask.Response(
                    status=200,
                    response=json.dumps(
                        {"status": "BLOCKED", "reason": "DIALOGFLOW_API_DISABLED"}
                    ),
                )
            }
        elif (result.json()["error"]["status"] == "PERMISSION_DENIED") and (
            result.json()["error"]["message"].startswith(
                "Caller does not have required permission"
            )
        ):
            response = {
                "response": flask.Response(
                    status=200,
                    response=json.dumps(
                        {"status": "BLOCKED", "reason": "WRONG_PERMISSION"}
                    ),
                )
            }
        elif "details" in result.json()["error"]:
            response = None
            for details in result.json()["error"]["details"]:
                for violation in details["violations"]:
                    if violation["type"] == "VPC_SERVICE_CONTROLS":
                        response = {
                            "response": flask.Response(
                                status=200,
                                response=json.dumps(
                                    {
                                        "status": "BLOCKED",
                                        "reason": "VPC_SERVICE_CONTROLS",
                                    }
                                ),
                            )
                        }
            if response is None:
                response = {
                    "response": flask.Response(
                        status=200,
                        response=json.dumps(
                            {"status": "BLOCKED", "reason": "PERMISSION_DENIED"}
                        ),
                    )
                }
    elif result.status_code != 200:
        logger.info("  dialogflow API rejected request: %s", result.text)
        response = {
            "response": flask.Response(
                status=result.status_code, response=json.dumps({"error": result.text})
            )
        }
    else:
        result_dict = result.json()
        if len(result_dict) == 0:
            response = {
                "response": flask.Response(
                    status=200,
                    response=json.dumps(
                        {"status": "BLOCKED", "reason": "AGENT_NOT_FOUND"}
                    ),
                )
            }
        elif "error" in result_dict:
            logger.info("  get_agents error: %s", result.text)
            # Seems like a potential bug; returning a dict? Also error resulting from 200 code?
            response = None
        else:
            response = {
                "data": {data["displayName"]: data for data in result_dict["agents"]}
            }
    return response


def get_webhooks(token, agent_name, project_id, region):
    """Get webhooks using dialogflow API."""
    headers = {}
    headers["x-goog-user-project"] = project_id
    headers["Authorization"] = f"Bearer {token}"
    result = requests.get(
        f"https://{region}-dialogflow.googleapis.com/v3/{agent_name}/webhooks",
        headers=headers,
        timeout=10,
    )
    if result.status_code == 403:
        for details in result.json()["error"]["details"]:
            for violation in details["violations"]:
                if violation["type"] == "VPC_SERVICE_CONTROLS":
                    response = flask.Response(
                        status=200,
                        response=json.dumps(
                            {"status": "BLOCKED", "reason": "VPC_SERVICE_CONTROLS"}
                        ),
                    )
                    return {"response": response}
    if result.status_code != 200:
        logger.info("  dialogflow API rejected request: %s", result.text)
        response = flask.Response(
            status=result.status_code, response=json.dumps({"error": result.text})
        )
        return {"response": response}
    agents = result.json()
    if "webhooks" not in agents:
        return {
            "response": flask.Response(
                status=200,
                response=json.dumps(
                    {"status": "BLOCKED", "reason": "WEBHOOK_NOT_FOUND"}
                ),
            )
        }
    return {"data": {data["displayName"]: data for data in agents["webhooks"]}}


def get_token_and_project(request):
    """Helper method to retrieve a token or project, or return early."""
    response = {}
    token_dict = get_token.get_token(request, token_type="access_token")
    if "response" in token_dict:
        return token_dict
    response["token"] = token_dict["access_token"]

    response["project_id"] = request.args.get("project_id", None)
    if not response["project_id"]:
        return {
            "response": flask.Response(
                status=200,
                response=json.dumps({"status": "BLOCKED", "reason": "NO_PROJECT_ID"}),
            )
        }
    return response


def get_restricted_service_status(request, service_key):
    """Get status of restricted service:"""
    data = get_token_and_project(request)
    if "response" in data:
        return data["response"]
    project_id, token = data["project_id"], data["token"]
    access_policy_title = request.args.get("access_policy_title", None)

    response = get_access_policy_name(token, access_policy_title, project_id)
    if "response" in response:
        return response["response"]
    access_policy_name = response["access_policy_name"]
    status_dict = get_restricted_services_status(token, project_id, access_policy_name)
    if "response" in status_dict:
        return status_dict["response"]

    return flask.Response(
        status=200,
        response=json.dumps({"status": status_dict[service_key]}),
    )
