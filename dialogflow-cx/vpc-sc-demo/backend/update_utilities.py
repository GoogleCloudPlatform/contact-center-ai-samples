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

"""Utilities module for update_blueprint.py."""

import logging

import flask
import google.cloud.storage as storage  # pylint: disable=consider-using-from-import
import requests
import status_utilities as su
from google.oauth2 import credentials

logger = logging.getLogger(__name__)


def update_service_perimeter_status_inplace(  # pylint: disable=inconsistent-return-statements
    api, restrict_access, service_perimeter_status
):
    """Update security perimeter status dict; this function operates inplace."""
    if not restrict_access:
        if "restrictedServices" not in service_perimeter_status["status"]:
            return flask.Response(status=200)
        if api not in service_perimeter_status["status"]["restrictedServices"]:
            return flask.Response(status=200)
        service_perimeter_status["status"]["restrictedServices"] = [
            service
            for service in service_perimeter_status["status"]["restrictedServices"]
            if service != api
        ]
    else:
        if "restrictedServices" not in service_perimeter_status["status"]:
            service_perimeter_status["status"]["restrictedServices"] = [api]
        elif api in service_perimeter_status["status"]["restrictedServices"]:
            return flask.Response(status=200)
        else:
            service_perimeter_status["status"]["restrictedServices"].append(api)


def get_service_perimeter_data(request):
    """Get data needed for update_security_perimeter."""
    data = su.get_token_and_project(request)
    if "response" in data:
        return {"response": data["response"]}
    access_policy_title = request.args["access_policy_title"]
    response = su.get_access_policy_name(
        data["token"],
        access_policy_title,
        data["project_id"],
    )
    if "response" in response:
        return {"response": response["response"]}
    data["access_policy_name"] = response["access_policy_name"]
    data["restrict_access"] = request.get_json(silent=True)["status"]
    return data


def update_security_perimeter(request, api):
    """Update security perimeter."""

    data = get_service_perimeter_data(request)
    if "response" in data:
        return data["response"]
    token = data["token"]
    project_id = data["project_id"]
    restrict_access = data["restrict_access"]
    access_policy_name = data["access_policy_name"]

    service_perimeter_status = su.get_service_perimeter_status(
        token, project_id, access_policy_name
    )
    response = update_service_perimeter_status_inplace(
        api, restrict_access, service_perimeter_status
    )
    if response:
        return response

    headers = {}
    headers["x-goog-user-project"] = project_id
    headers["Authorization"] = f"Bearer {token}"
    response = su.get_service_perimeter_data_uri(token, project_id, access_policy_name)
    if "response" in response:
        return response
    service_perimeter_data_uri = response["uri"]
    result = requests.patch(
        service_perimeter_data_uri,
        headers=headers,
        json=service_perimeter_status,
        params={"updateMask": "status.restrictedServices"},
        timeout=10,
    )
    if result.status_code != 200:
        logger.info(
            "  accesscontextmanager API rejected PATCH request: %s", result.text
        )
        return flask.Response(status=result.status_code, response=result.text)
    return flask.Response(status=200)


def get_cert(token, project_id, bucket):
    """Utility method to get cert file from bucket."""
    curr_credentials = credentials.Credentials(token)
    bucket_obj = storage.Client(
        project=project_id, credentials=curr_credentials
    ).bucket(bucket)
    blob = storage.blob.Blob("server.der", bucket_obj)
    return blob.download_as_string()
