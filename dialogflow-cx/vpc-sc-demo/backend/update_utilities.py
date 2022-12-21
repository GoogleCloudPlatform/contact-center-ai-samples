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
import requests

import status_utilities as su


logger = logging.getLogger(__name__)


def update_service_perimeter_status_inplace(  # pylint: disable=inconsistent-return-statements
    api,
    restrict_access,
    service_perimeter_status
):
    """Update security perimeter status dict; this function operates inplace."""
    if not restrict_access:
        if 'restrictedServices' not in service_perimeter_status['status']:
            return flask.Response(status=200)
        if api not in service_perimeter_status['status']['restrictedServices']:
            return flask.Response(status=200)
        service_perimeter_status['status']['restrictedServices'] = [
            service for service in service_perimeter_status['status']['restrictedServices']
            if service != api
        ]
    else:
        if 'restrictedServices' not in service_perimeter_status['status']:
            service_perimeter_status['status']['restrictedServices'] = [api]
        elif api in service_perimeter_status['status']['restrictedServices']:
            return flask.Response(status=200)
        else:
            service_perimeter_status['status']['restrictedServices'].append(api)


def update_security_perimeter(token, api, restrict_access, project_id, access_policy_name):
    """Update security perimeter."""
    service_perimeter_status = su.get_service_perimeter_status(
        token,
        project_id,
        access_policy_name
    )
    response = update_service_perimeter_status_inplace(
        api,
        restrict_access,
        service_perimeter_status
    )
    if response:
        return response

    headers = {}
    headers["x-goog-user-project"] = project_id
    headers['Authorization'] = f'Bearer {token}'
    response = su.get_service_perimeter_data_uri(token, project_id, access_policy_name)
    if 'response' in response:
        return response
    service_perimeter_data_uri = response['uri']
    result = requests.patch(
        service_perimeter_data_uri,
        headers=headers,
        json=service_perimeter_status,
        params={
            'updateMask': 'status.restrictedServices'},
        timeout=10,
    )
    if result.status_code != 200:
        logger.info('  accesscontextmanager API rejected PATCH request: %s', result.text)
        return flask.Response(status=result.status_code, response=result.text)
    return flask.Response(status=200)
