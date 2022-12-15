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

import logging

import flask

launchpad = flask.Blueprint("launchpad", __name__)
logger = logging.getLogger(__name__)

@launchpad.route('/get_principal', methods=['GET'])
def get_principal():
  token_dict = get_token(request, token_type='email')
  if 'response' in token_dict:
    return redirect(url_for('logout'))
  return Response(status=200, response=json.dumps({'principal': token_dict['email']}))
  

@launchpad.route('/validate_project_id', methods=['GET'])
def validate_project_id():
  project_id = request.args.get('project_id', None)
  app.logger.info(f'project_id to validate: "{project_id}"')
  if not project_id:
    app.logger.info(f'project_id empty')
    return Response(status=200, response=json.dumps({'status':False}, indent=2))
  token_dict = get_token(request, token_type='access_token')
  if 'response' in token_dict:
    app.logger.info(f'ERROR TO DEBUG: {token_dict["response"]}')
    return token_dict['response']
  access_token = token_dict['access_token']

  headers = {}
  headers['Authorization'] = f'Bearer {access_token}'
  r = requests.get(f'https://cloudresourcemanager.googleapis.com/v1/projects/{project_id}', headers=headers)

  if r.status_code == 200:
    return Response(status=200, response=json.dumps({'status':True}, indent=2))
  else:
    app.logger.info(f'cloudresourcemanager request not 200: {r.text}')
    return Response(status=200, response=json.dumps({'status':False}, indent=2))