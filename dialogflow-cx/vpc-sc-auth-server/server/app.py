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

"""Authentication server for VPC-SC Live Demo."""

import io
import json
import os
from base64 import b64decode
from zipfile import ZipFile

import google.auth
import requests
import session
from flask import Flask, Response, redirect, request, send_file
from flask.logging import create_logger  # pylint: disable=ungrouped-imports
from google.auth.transport import requests as reqs
from google.oauth2 import id_token
from utilities import access_secret_version

app = Flask(__name__)
logger = create_logger(app)
credentials, project_id = google.auth.default()


def get_redirect_url():
    """Get the redirect URL, depending on prod vs dev deployment."""
    debug_port = os.getenv("DEBUG_PORT")
    if os.getenv("PROD") == "true":
        return "https://auth.dialogflow-demo.app/callback"
    return f"http://localhost:{debug_port}/callback"


@app.route("/callback")
def callback():
    """Callback route, redirects to the user-provided return_to URL."""
    args = request.args.to_dict()
    state = json.loads(b64decode(args["state"]))
    redirect_path = state["return_to"]
    session_id = state["session_id"]
    data = {
        "code": args["code"],
        "client_id": os.getenv("CLIENT_ID"),
        "client_secret": access_secret_version(
            project_id, "application-client-secret", "latest"
        )["response"],
        "redirect_uri": get_redirect_url(),
        "grant_type": "authorization_code",
    }

    resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data=data,
        timeout=10,
    ).json()

    info = id_token.verify_oauth2_token(resp["id_token"], reqs.Request())

    session.create(
        {
            "id_token": resp["id_token"],
            "access_token": resp["access_token"],
            "refresh_token": resp["refresh_token"],
            "email": info["email"],
            "expiration": info["exp"],
            "origin": redirect_path,
        },
        session_id=session_id,
        public_pem=state["public_pem"],
    )

    if session_id is None:
        logger.critical("Could not create session")
        return Response(status=403)

    response = redirect(redirect_path)
    return response


@app.route("/login", methods=["GET"])
def login_get():
    """login_get
    Handles requests made to the path /login. This may occur due to a user
    following a link, or other website pages redirecting here.
    The request may include a query parameter called return_to, which will lead
    to the user being directed to that path following a successful login. This
    path is relative to the application's root URL and special characters must
    be url-encoded.
    Example:
        GET /login?return_to=/
    """
    state = request.args["state"]
    # Link to redirect to Google auth service, including required query parameters.
    sign_in_url = "https://accounts.google.com/o/oauth2/v2/auth?"

    # Client apps and their callbacks must be registered and supplied here
    sign_in_url += f"redirect_uri={get_redirect_url()}&"
    sign_in_url += f'client_id={os.getenv("CLIENT_ID")}&'

    # Asking for user email and any previously granted scopes openid%20email
    sign_in_url += "scope=openid%20"
    sign_in_url += "email%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcloud-platform&"
    sign_in_url += "include_granted_scopes=true&"

    # The next two parameters are essential to get a refresh token
    sign_in_url += "prompt=consent&"
    sign_in_url += "access_type=offline&"

    # Asking for a code that can then be exchanged for user information
    sign_in_url += "response_type=code&"

    # Remember this info and echo it back to me so I'll know what to do next
    sign_in_url += f"state={state}&"

    return redirect(sign_in_url)


@app.route("/auth", methods=["GET"])
def auth():
    """Rout for getting authentication information, when session_id is valid."""
    # pylint: disable=unexpected-keyword-arg
    session_id = request.args.get("session_id")

    session_data = session.read(session_id)
    if "error" in session_data:
        return session_data["error"]

    zip_file_stream = io.BytesIO()
    with ZipFile(zip_file_stream, "w") as zip_file:
        for (
            curr_stream_name,
            curr_stream,
        ) in session_data.items():
            zip_file.writestr(
                os.path.basename(curr_stream_name), curr_stream.getvalue()
            )
    zip_file_stream.seek(0)

    return send_file(
        zip_file_stream,
        as_attachment=True,
        attachment_filename="encrypted_session.zip",
    )


if __name__ == "__main__":  # pragma: no cover
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
