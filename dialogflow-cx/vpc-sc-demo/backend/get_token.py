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

"""Module to get a stored token from the VPC-SC Demo Auth Server."""

import collections


class LRU:
  """Quick implementation of an LRU cache."""
 
  def __init__(self, func, max_size=128):
    self.cache = collections.OrderedDict()
    self.func = func
    self.max_size = max_size

  def __call__(self, *args):
    cache = self.cache
    if args in cache:
      cache.move_to_end(args)
      return cache[args]
    result = self.func(*args)
    cache[args] = result
    if len(cache) > self.max_size:
      cache.popitem(last=False)
    return result


def get_token_from_auth_server(session_id, origin):
  """Retrieve a stored token from the VPC-SC Demo Auth Server."""

  params = {
    'session_id': session_id,
    'origin': origin,
  }

  r = requests.get(AUTH_SERVICE_AUTH_ENDPOINT, params=params)
  if r.status_code == 401:
    app.logger.info(f'  auth-service "{AUTH_SERVICE_AUTH_ENDPOINT}" rejected request: {r.text}')
    return {'response': Response(status=500, response=json.dumps({'status':'BLOCKED', 'reason':'REJECTED_REQUEST'}))}

  zf = zipfile.ZipFile(io.BytesIO(r.content))
  key_bytes_stream = zf.open('key').read()
  decrypt = PKCS1_OAEP.new(key=pr_key)
  decrypted_message = decrypt.decrypt(key_bytes_stream)
  aes_cipher = AESCipher(key=decrypted_message)
  auth_data = json.loads(aes_cipher.decrypt(zf.open('session_data').read()).decode())

  return {'auth_data': auth_data}


def get_token(request, token_type='access', cache=LRU(get_token_from_auth_server) ):
  """Get a stored token from the VPC-SC Demo Auth Server, or from local cache."""

  if not request.cookies.get("session_id"):
    app.logger.info(f'get_token request did not have a session_id')
    return {'response': Response(status=200, response=json.dumps({'status':'BLOCKED', 'reason':'BAD_SESSION_ID'}))}

  session_id = request.cookies.get("session_id")
  origin = request.host_url

  response = cache(session_id, origin)
  if 'response' in response:
    cache.cache.pop((session_id, origin))
    return response
  auth_data = response['auth_data']

  try:
    info = id_token.verify_oauth2_token(auth_data['id_token'], reqs.Request())
  except ValueError as e:
    if "Token expired" in str(e):
      app.logger.info(f'  auth-service token expired')
      return {'response': Response(status=200, response=json.dumps({'status':'BLOCKED', 'reason':'TOKEN_EXPIRED'}))}
    else:
      response = f'  auth-service ValueError: {r.text}'
      app.logger.info(response)
      return {'response': Response(status=500, response=json.dumps({'status':'BLOCKED', 'reason':response.lstrip()}))}

  if info['email_verified'] != True:
    app.logger.info(f'  oauth error: email not verified')
    return {'response': Response(status=500, response=json.dumps({'status':'BLOCKED', 'reason':'BAD_EMAIL'}))}

  response = {}
  if token_type == 'access_token':
    response['access_token'] = auth_data['access_token']
  elif token_type == 'id_token':
    response['id_token'] = auth_data['id_token']
  elif token_type == 'email':
    response['email'] = auth_data['email']
  else:
    response = f'  Requested token_type "{token_type}" not one of ["access_token","id_token","email"]'
    app.logger.info(response)
    return {'response': Response(status=500, response=json.dumps({'status':'BLOCKED', 'reason':response.lstrip()}))}
  return response
