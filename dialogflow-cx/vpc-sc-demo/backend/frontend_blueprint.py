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

import os

import flask

STATIC_FOLDER = "frontend/build"

frontend = flask.Blueprint("frontend", __name__, static_folder=STATIC_FOLDER)


@frontend.route("/", defaults={"path": ""})
@frontend.route("/<path:path>")
def root(path):
    """Serve static frontend."""
    if path != "" and os.path.exists(frontend.static_folder + "/" + path):
        return flask.send_from_directory(frontend.static_folder, path)
    return flask.send_from_directory(frontend.static_folder, "index.html")
