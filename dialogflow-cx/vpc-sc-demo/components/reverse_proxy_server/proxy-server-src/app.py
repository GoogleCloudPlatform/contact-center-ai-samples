# Copyright 2022 Google LLC
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
# pylint: disable=E1101

"""Reverse proxy server to redirect incoming requests to a webhook trigger uri."""

import logging
import os
import signal

import google.auth
import requests
from flask import Flask, Response, abort, request
from google.auth.transport import requests as reqs
from google.oauth2 import id_token

app = Flask(__name__)
gunicorn_logger = logging.getLogger("gunicorn.error")
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

authorized_emails = [os.environ["BOT_USER"]]


@app.before_request
def check_user_authentication():  # pylint: disable=R1710
    """Validates that caller is in the allowslist authorized_emails."""
    # pylint: disable=logging-fstring-interpolation
    app.logger.info("[0] Begin check_user_authentication")

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
    app.logger.info(f"[0]   User: {verified_email}")
    if verified_email not in authorized_emails:
        return abort(403)


@app.post("/")
def root() -> Response:
    """Redirect request to webhook trigger."""
    app.logger.info('Endpoint "webhook" triggered')
    audience = os.environ["WEBHOOK_TRIGGER_URI"]
    app.logger.info("WEBHOOK_TRIGGER_URI: %s", audience)
    auth_req = google.auth.transport.requests.Request()
    token = id_token.fetch_id_token(auth_req, audience)
    new_headers = {}
    new_headers["Content-type"] = "application/json"
    new_headers["Authorization"] = f"Bearer {token}"
    result = requests.post(
        audience, json=request.get_json(), headers=new_headers, timeout=10
    )
    if result.status_code != 200:
        app.logger.info("Webhook Response error code: %s", result.status_code)
        app.logger.info("Webhook Response error %s", result.text)
    else:
        app.logger.info("Webhook Response: %s", result.status_code)

    return Response(status=result.status_code, response=result.text)


def shutdown_handler(signal_int, frame) -> None:
    """Safely exit program"""
    # pylint: disable=logging-fstring-interpolation
    del frame
    app.logger.info(f"Caught Signal {signal.strsignal(signal_int)}")
    raise SystemExit(0)


if __name__ == "__main__":  # pragma: no cover
    # Running application locally, outside of a Google Cloud Environment

    # handles Ctrl-C termination
    signal.signal(signal.SIGINT, shutdown_handler)

    app.run(host="localhost", port=8080, debug=False)
else:
    # handles Cloud Run container termination
    signal.signal(signal.SIGTERM, shutdown_handler)
