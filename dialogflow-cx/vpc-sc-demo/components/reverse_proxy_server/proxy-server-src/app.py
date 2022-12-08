# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import signal
import sys
import os
from types import FrameType

import requests
import logging


from flask import Flask, request, abort

from google.auth.transport import requests as reqs
from google.oauth2 import id_token
import google.auth.transport.requests
import os


app = Flask(__name__)
gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

authorized_emails = [
    os.environ['BOT_USER']
]

@app.before_request
def check_user_authentication():
    app.logger.info('[0] Begin check_user_authentication')
    

    verified_email = None

    auth = request.headers.get("Authorization", None)

    if auth is None:
        return abort(403)

    if not auth.startswith("Bearer "):
        return abort(403)

    token = auth[7:]  # Remove "Bearer: " prefix

    # Extract the email address from the token. Since there may be
    # two types of token provided (Firebase or Google OAuth2) and
    # failed verification raises an exception, need multiple
    # try/except blocks.

    info = None
    try:
        info = id_token.verify_firebase_token(token, reqs.Request())
    except ValueError:
        pass

    try:
        if info is None:
            info = id_token.verify_oauth2_token(token, reqs.Request())
    except ValueError:
        pass

    if info is None:
        return abort(403)

    if "email" not in info:
        return abort(403)
        
    verified_email = info["email"]
    app.logger.info(f'[0]   User: {verified_email}')
    if verified_email not in authorized_emails:
        return abort(403)


@app.post("/")
def webhook() -> str:

    app.logger.info('Endpoint "webhook" triggered')
    audience = os.environ["WEBHOOK_TRIGGER_URI"]
    auth_req = google.auth.transport.requests.Request()
    token = google.oauth2.id_token.fetch_id_token(auth_req, audience)
    new_headers = {}
    new_headers['Content-type'] = 'application/json'
    new_headers['Authorization'] = f'Bearer {token}'
    result = requests.post(audience, json=request.get_json(), headers=new_headers)
    return result.text


def shutdown_handler(signal_int: int, frame: FrameType) -> None:
    app.logger.info(f"Caught Signal {signal.strsignal(signal_int)}")

    from utils.logging import flush

    flush()

    # Safely exit program
    sys.exit(0)


if __name__ == "__main__":
    # Running application locally, outside of a Google Cloud Environment

    # handles Ctrl-C termination
    signal.signal(signal.SIGINT, shutdown_handler)

    app.run(host="localhost", port=8080, debug=True)
else:
    # handles Cloud Run container termination
    signal.signal(signal.SIGTERM, shutdown_handler)
