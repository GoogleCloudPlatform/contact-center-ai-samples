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

import json
import logging

import flask
import requests

logger = logging.getLogger(__name__)


def get_project_number(token, project_id):

    headers = {}
    headers["Content-type"] = "application/json"
    headers["Authorization"] = f"Bearer {token}"
    r = requests.get(
        f"https://cloudresourcemanager.googleapis.com/v1/projects/{project_id}",
        headers=headers,
    )
    if "projectNumber" in r.json():
        return {"project_number": r.json()["projectNumber"]}
    else:
        return {
            "response": flask.Response(
                status=200,
                response=json.dumps({"status": "BLOCKED", "reason": "NO_PROJECT"}),
            )
        }


def get_access_policy_name(token, access_policy_title, project_id):

    if not access_policy_title:
        return {
            "response": flask.Response(
                status=200,
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
    )

    if response.status_code != 200:
        return {"response": flask.Response(status=500, response=json.dumps(
            {
                "status": "BLOCKED", 
                "reason": json.loads(response.text)["error"].get("status", "UNKNOWN_STATUS")
            }))
        }

    organization_id = None
    for ancestor_dict in response.json().get("ancestor", []):
        if ancestor_dict["resourceId"]["type"] == "organization":
            organization_id = ancestor_dict["resourceId"]["id"]
    if not organization_id:
        return {
            "response": flask.Response(
                status=200,
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
        f"https://accesscontextmanager.googleapis.com/v1/accessPolicies?parent=organizations/{organization_id}",
        headers=headers,
    )

    for policy in response.json().get("accessPolicies", []):
        if policy["title"] == access_policy_title:
            if f"projects/{project_number}" in policy["scopes"]:
                return {"access_policy_name": policy["name"]}

    return {
        "response": flask.Response(
            status=200,
            response=json.dumps({"status": "BLOCKED", "reason": "POLICY_NOT_FOUND"}),
        )
    }


def get_service_perimeter_data_uri(token,
        project_id,
        access_policy_name,
        perimeter_title="df_webhook",
    ):
    access_policy_id = access_policy_name.split("/")[1]
    headers = {}
    headers["x-goog-user-project"] = project_id
    headers["Authorization"] = f"Bearer {token}"
    response = requests.get(
        f"https://accesscontextmanager.googleapis.com/v1/accessPolicies/{access_policy_id}/servicePerimeters",
        headers=headers,
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
        else:
            logger.info(f"  accesscontextmanager API rejected request: {response.text}")
            return {"response": flask.Response(status=500, response=response.text)}

    for service_perimeter_dict in response.json().get("servicePerimeters", []):
        if service_perimeter_dict["title"] == perimeter_title:
            return {
                "uri": f'https://accesscontextmanager.googleapis.com/v1/{service_perimeter_dict["name"]}'
            }

    return {
        "response": flask.Response(
            status=200,
            response=json.dumps({"status": "BLOCKED", "reason": "PERIMETER_NOT_FOUND"}),
        )
    }


def get_service_perimeter_status(token, project_id, access_policy_name):
    headers = {}
    headers["x-goog-user-project"] = project_id
    headers["Authorization"] = f"Bearer {token}"
    response = get_service_perimeter_data_uri(token, project_id, access_policy_name)
    if "response" in response:
        return response
    service_perimeter_data_uri = response["uri"]
    r = requests.get(service_perimeter_data_uri, headers=headers)
    if r.status_code != 200:
        logger.info(f"  accesscontextmanager API rejected request: {r.text}")
        if (r.json()["error"]["status"] == "PERMISSION_DENIED") and (
            r.json()["error"]["message"].startswith(
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
        if r.json()["error"]["status"] == "PERMISSION_DENIED":
            response = flask.Response(
                status=200,
                response=json.dumps(
                    {"status": "BLOCKED", "reason": "PERMISSION_DENIED"}
                ),
            )
            return {"response": response}
        else:
            response = flask.Response(status=r.status_code, response=r.text)
            return {"response": response}
    return r.json()


def get_restricted_services_status(token, project_id, access_policy_name):
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

    headers = {}
    headers["x-goog-user-project"] = project_id
    headers["Authorization"] = f"Bearer {token}"
    r = requests.get(
        f"https://cloudfunctions.googleapis.com/v1/projects/{project_id}/locations/{region}/functions/{function_name}",
        headers=headers,
    )
    if r.status_code == 200:
        return {"status": "OK"}
    elif r.status_code == 404 and r.json()["error"]["status"] == "NOT_FOUND":
        return {
            "response": flask.Response(
                status=200,
                response=json.dumps(
                    {"status": "BLOCKED", "reason": "WEBHOOK_NOT_FOUND"}
                ),
            )
        }
    elif r.status_code == 403 and r.json()["error"]["message"].startswith(
        "Cloud Functions API has not been used in project"
    ):
        return {
            "response": flask.Response(
                status=200,
                response=json.dumps(
                    {"status": "BLOCKED", "reason": "CLOUDFUNCTIONS_API_DISABLED"}
                ),
            )
        }
    elif r.status_code == 403:
        if (r.json()["error"]["status"] == "PERMISSION_DENIED") and (
            r.json()["error"]["message"].startswith(
                "Permission 'cloudfunctions.functions.get' denied on resource"
            )
        ):
            return {
                "response": flask.Response(
                    status=200,
                    response=json.dumps(
                        {"status": "BLOCKED", "reason": "PERMISSION_DENIED"}
                    ),
                )
            }
        for details in r.json()["error"]["details"]:
            for violation in details["violations"]:
                if violation["type"] == "VPC_SERVICE_CONTROLS":
                    return {
                        "response": flask.Response(
                            status=200,
                            response=json.dumps(
                                {"status": "BLOCKED", "reason": "VPC_SERVICE_CONTROLS"}
                            ),
                        )
                    }
        return {"response": flask.Response(status=500, response=r.text)}
    else:
        return {"response": flask.Response(status=500, response=json.dumps(r.json()))}


def get_agents(token, project_id, region):
    headers = {}
    headers["x-goog-user-project"] = project_id
    headers["Authorization"] = f"Bearer {token}"
    r = requests.get(
        f"https://{region}-dialogflow.googleapis.com/v3/projects/{project_id}/locations/{region}/agents",
        headers=headers,
    )
    if r.status_code == 403:
        if (r.json()["error"]["status"] == "PERMISSION_DENIED") and (
            r.json()["error"]["message"].startswith(
                "Dialogflow API has not been used in project"
            )
        ):
            response = flask.Response(
                status=200,
                response=json.dumps(
                    {"status": "BLOCKED", "reason": "DIALOGFLOW_API_DISABLED"}
                ),
            )
            return {"response": response}
        if (r.json()["error"]["status"] == "PERMISSION_DENIED") and (
            r.json()["error"]["message"].startswith(
                "Caller does not have required permission"
            )
        ):
            response = flask.Response(
                status=200,
                response=json.dumps(
                    {"status": "BLOCKED", "reason": "WRONG_PERMISSION"}
                ),
            )
            return {"response": response}
        for details in r.json()["error"]["details"]:
            for violation in details["violations"]:
                if violation["type"] == "VPC_SERVICE_CONTROLS":
                    return {
                        "response": flask.Response(
                            status=200,
                            response=json.dumps(
                                {"status": "BLOCKED", "reason": "VPC_SERVICE_CONTROLS"}
                            ),
                        )
                    }
        if r.json()["error"]["status"] == "PERMISSION_DENIED":
            response = flask.Response(
                status=200,
                response=json.dumps(
                    {"status": "BLOCKED", "reason": "PERMISSION_DENIED"}
                ),
            )
            return {"response": response}
    elif r.status_code != 200:
        logger.info(f"  dialogflow API rejected request: {r.text}")
        response = flask.Response(status=r.status_code, response=r.text)
        return {"response": response}
    result_dict = r.json()
    if len(result_dict) == 0:
        return {
            "response": flask.Response(
                status=200,
                response=json.dumps({"status": "BLOCKED", "reason": "AGENT_NOT_FOUND"}),
            )
        }
    if "error" in result_dict:
        logger.info(f"  get_agents error: {r.text}")
        # Seems like a potential bug; should be returning a dict, and error resulting from 200 code.
        return None
    return {"data": {data["displayName"]: data for data in result_dict["agents"]}}


def get_webhooks(token, agent_name, project_id, region):
    headers = {}
    headers["x-goog-user-project"] = project_id
    headers["Authorization"] = f"Bearer {token}"
    r = requests.get(
        f"https://{region}-dialogflow.googleapis.com/v3/{agent_name}/webhooks",
        headers=headers,
    )
    if r.status_code == 403:
        for details in r.json()["error"]["details"]:
            for violation in details["violations"]:
                if violation["type"] == "VPC_SERVICE_CONTROLS":
                    response = flask.Response(
                        status=200,
                        response=json.dumps(
                            {"status": "BLOCKED", "reason": "VPC_SERVICE_CONTROLS"}
                        ),
                    )
                    return {"response": response}
    if r.status_code != 200:
        logger.info(f"  dialogflow API rejected request: {r.text}")
        response = flask.Response(status=r.status_code, response=r.text)
        return {"response": response}
    agents = r.json()
    return {"data": {data["displayName"]: data for data in agents["webhooks"]}}
