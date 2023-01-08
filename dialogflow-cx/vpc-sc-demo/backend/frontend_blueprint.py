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


"""Blueprint for serving static frontend."""

import logging
import os

import analytics_utilities as au
import flask
import werkzeug

STATIC_FOLDER = "/frontend/build"

frontend = flask.Blueprint("frontend", __name__, static_folder=STATIC_FOLDER)
logger = logging.getLogger(__name__)


@frontend.route("/", defaults={"path": ""})
@frontend.route("/<path:path>")
def root(path):
    """Serve static frontend."""
    secure_path = werkzeug.utils.secure_filename(path)
    if secure_path != "" and os.path.exists(
        os.path.join(frontend.static_folder, secure_path)
    ):
        return flask.send_from_directory(frontend.static_folder, secure_path)

    response = flask.send_from_directory(frontend.static_folder, "index.html")
    return au.register_action(
        flask.request, response, au.ACTIONS.UPDATE_STATUS, {"service": "ingress"}
    )
