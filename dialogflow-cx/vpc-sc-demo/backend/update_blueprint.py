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

import logging
import json
import base64

import flask
import requests
from google.oauth2 import credentials
from google.cloud import storage

import get_token
import status_utilities as su
import update_utilities as uu


DOMAIN = 'webhook.internal'
update = flask.Blueprint("update", __name__)
logger = logging.getLogger(__name__)


@update.route('/update_webhook_access', methods=['POST'])
def update_webhook_access():
  data = su.get_token_and_project(flask.request)
  if "response" in data:
      return data["response"]
  project_id, token = data["project_id"], data["token"]
  region = flask.request.args["region"]
  webhook_name = flask.request.args['webhook_name']
  content = flask.request.get_json(silent=True)
  internal_only = content['status']

  headers = {}
  headers["x-goog-user-project"] = project_id
  headers['Authorization'] = f'Bearer {token}'
  r = requests.get(f'https://cloudfunctions.googleapis.com/v2/projects/{project_id}/locations/{region}/functions/{webhook_name}:getIamPolicy', headers=headers)
  if r.status_code != 200:
    logger.info(f'  cloudfunctions API rejected getIamPolicy GET request: {r.text}')
    return flask.Response(status=r.status_code, response=r.text)

  policy_dict = r.json()
  allUsers_is_invoker_member = False
  for binding in policy_dict.get('bindings', []):
    for member in binding['members']:
      if member == "allUsers" and binding['role'] == "roles/cloudfunctions.invoker":
        allUsers_is_invoker_member = True
  if (
    (not internal_only and allUsers_is_invoker_member) or 
    ((internal_only) and (not allUsers_is_invoker_member))
  ):
    # internal_only matches request; no change needed
    return flask.Response(status=200)

  if internal_only:
    for binding in policy_dict.get('bindings', []):
      for member in binding['members']:
        if binding['role'] == "roles/cloudfunctions.invoker":
          binding['members'] = [member for member in binding['members'] if member != 'allUsers']
  else:
    if 'bindings' not in policy_dict or len(policy_dict['bindings']) == 0:
      policy_dict['bindings'] = [{'role': 'roles/cloudfunctions.invoker', 'members': []}]
    invoker_role_exists = None
    for binding in policy_dict['bindings']:
      if binding['role'] == 'roles/cloudfunctions.invoker':
        invoker_role_exists = True
        binding['members'].append('allUsers')
    if not invoker_role_exists:
      policy_dict['bindings'].append({'role': 'roles/cloudfunctions.invoker', 'members': ['allUsers']})
  r = requests.post(f'https://cloudfunctions.googleapis.com/v1/projects/{project_id}/locations/{region}/functions/{webhook_name}:setIamPolicy', headers=headers, json={'policy':policy_dict})
  if r.status_code != 200:
    logger.info(f'  cloudfunctions API rejected setIamPolicy POST request: {r.text}')
    return flask.Response(status=r.status_code, response=r.text)
  return flask.Response(status=200)


@update.route('/update_webhook_ingress', methods=['POST'])
def update_webhook_ingress():
  data = su.get_token_and_project(flask.request)
  if "response" in data:
      return data["response"]
  project_id, token = data["project_id"], data["token"]
  region = flask.request.args["region"]
  webhook_name = flask.request.args['webhook_name']
  content = flask.request.get_json(silent=True)

  headers = {}
  headers['Content-type'] = 'application/json'
  headers["x-goog-user-project"] = project_id
  headers['Authorization'] = f'Bearer {token}'
  r = requests.get(f'https://cloudfunctions.googleapis.com/v1/projects/{project_id}/locations/{region}/functions/{webhook_name}', headers=headers)
  if r.status_code != 200:
    logger.info(f'  cloudfunctions API rejected GET request: {r.text}')
    return flask.Response(status=r.status_code, response=r.text)

  webhook_data = r.json()
  ingress_settings = "ALLOW_INTERNAL_ONLY" if content['status'] else "ALLOW_ALL"
  if webhook_data['ingressSettings'] == ingress_settings:
    return flask.Response(status=200)
  
  webhook_data['ingressSettings'] = ingress_settings
  r = requests.patch(f'https://cloudfunctions.googleapis.com/v1/projects/{project_id}/locations/{region}/functions/{webhook_name}', headers=headers, json=webhook_data)
  if r.status_code != 200:
    logger.info(f'  cloudfunctions API rejected PATCH request: {r.text}')
    return flask.Response(status=r.status_code, response=r.text)
  return flask.Response(status=200)




@update.route('/update_security_perimeter_cloudfunctions', methods=['POST'])
def update_security_perimeter_cloudfunctions():
  data = su.get_token_and_project(flask.request)
  if "response" in data:
      return data["response"]
  project_id, token = data["project_id"], data["token"]

  access_policy_title = flask.request.args['access_policy_title']
  response = su.get_access_policy_name(token, access_policy_title, project_id)
  if 'response' in response:
    return response['response']
  access_policy_name = response['access_policy_name']

  content = flask.request.get_json(silent=True)
  restrict_access = content['status']
  return uu.update_security_perimeter(token, 'cloudfunctions.googleapis.com', restrict_access, project_id, access_policy_name)


@update.route('/update_security_perimeter_dialogflow', methods=['POST'])
def update_security_perimeter_dialogflow():
  data = su.get_token_and_project(flask.request)
  if "response" in data:
      return data["response"]
  project_id, token = data["project_id"], data["token"]

  access_policy_title = flask.request.args['access_policy_title']
  response = su.get_access_policy_name(token, access_policy_title, project_id)
  if 'response' in response:
    return response['response']
  access_policy_name = response['access_policy_name']

  content = flask.request.get_json(silent=True)
  restrict_access = content['status']
  return uu.update_security_perimeter(token, 'dialogflow.googleapis.com', restrict_access, project_id, access_policy_name)

@update.route('/update_service_directory_webhook_fulfillment', methods=['POST'])
def update_service_directory_webhook_fulfillment():
  data = su.get_token_and_project(flask.request)
  if "response" in data:
      return data["response"]
  project_id, token = data["project_id"], data["token"]
  region = flask.request.args["region"]

  content = flask.request.get_json(silent=True)
  if content['status'] == True:
    fulfillment = 'service-directory'
  else:
    fulfillment = 'generic-web-service'

  bucket = flask.request.args['bucket']
  region = flask.request.args['region']
  webhook_name = flask.request.args['webhook_name']
  service_directory_namespace = "df-namespace"
  service_directory_service = "df-service"
  webhook_trigger_uri = f'https://{region}-{project_id}.cloudfunctions.net/{webhook_name}'

  result = su.get_agents(token, project_id, region)
  if 'response' in result:
    return result['response']
  agent_name = result['data']['Telecommunications']['name']
  result = su.get_webhooks(token, agent_name, project_id, region)
  if 'response' in result:
    return result['response']
  webhook_dict = result['data']['cxPrebuiltAgentsTelecom']
  webhook_name = webhook_dict['name']
  if fulfillment=='generic-web-service':
    data = {"displayName": "cxPrebuiltAgentsTelecom", "genericWebService": {"uri": webhook_trigger_uri}}
  elif fulfillment=='service-directory':
    def b64Encode(msg_bytes):
      base64_bytes = base64.b64encode(msg_bytes)
      return base64_bytes.decode('ascii')
    curr_credentials = credentials.Credentials(token)  
    BUCKET = storage.Client(project=project_id, credentials=curr_credentials).bucket(bucket)
    blob = storage.blob.Blob(f'server.der', BUCKET)
    allowed_ca_cert = blob.download_as_string()
    data = {
      "displayName": "cxPrebuiltAgentsTelecom", 
      "serviceDirectory": {
        "service": f'projects/{project_id}/locations/{region}/namespaces/{service_directory_namespace}/services/{service_directory_service}',
        "genericWebService": {
          "uri": f'https://{DOMAIN}',
          "allowedCaCerts": [b64Encode(allowed_ca_cert)]
        }
      }
    }
  else:
    return flask.Response(status=500, response=f'Unexpected setting for fulfillment: {fulfillment}')


  headers = {}
  headers["x-goog-user-project"] = project_id
  headers['Authorization'] = f'Bearer {token}'
  r = requests.patch(f'https://{region}-dialogflow.googleapis.com/v3/{webhook_name}', headers=headers, json=data)
  if r.status_code != 200:
    logger.info(f'  dialogflow API unexpectedly rejected invocation POST request: {r.text}')
    return flask.abort(r.status_code)
  
  return flask.Response(status=200)