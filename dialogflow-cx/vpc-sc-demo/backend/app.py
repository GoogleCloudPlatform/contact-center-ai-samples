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

"""VPC-SC Demo Server."""

import logging

import session_utilities as su
from analytics_blueprint import analytics
from asset_blueprint import asset
from flask import Flask
from frontend_blueprint import frontend
from launchpad_blueprint import launchpad
from session_blueprint import session
from status_blueprint import status
from update_blueprint import update

STATIC_FOLDER = "/frontend/build/static"


def configure_logging():
    """Set up logging for webserver."""
    level = logging.ERROR if su.is_prod() else logging.DEBUG
    logging.basicConfig(level=level)
    logging.getLogger("werkzeug").setLevel(level)


def create_app():
    """Create the webserver, register blueprints."""
    curr_app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path="/static")
    curr_app.register_blueprint(frontend)
    curr_app.register_blueprint(session)
    curr_app.register_blueprint(launchpad)
    curr_app.register_blueprint(status)
    curr_app.register_blueprint(asset)
    curr_app.register_blueprint(update)
    curr_app.register_blueprint(analytics)
    configure_logging()
    return curr_app


app = create_app()


if __name__ == "__main__":  # pragma: no cover
    app.run()
