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

"""Blueprint for analytics endpoints."""

import logging

import analytics_utilities as au
import flask

analytics = flask.Blueprint("analytics", __name__)
logger = logging.getLogger(__name__)


@analytics.route("/register_set_active_page", methods=["POST"])
def register_set_active_page():
    """Register set_active_page callback."""
    content = flask.request.get_json(silent=True)
    response = flask.Response(status=200)
    au.register_action(flask.request, response, au.ACTIONS.SET_ACTIVE_PAGE, content)
    return au.update_visit_cookie(flask.request, response)


@analytics.route("/register_set_active_tutorial_tab", methods=["POST"])
def register_set_active_tutorial_tab():
    """Register set_active_page callback."""
    content = flask.request.get_json(silent=True)
    response = flask.Response(status=200)
    au.register_action(
        flask.request, response, au.ACTIONS.SET_ACTIVE_TUTORIAL_TAB, content
    )
    return au.update_visit_cookie(flask.request, response)
