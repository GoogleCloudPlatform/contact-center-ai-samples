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

"""Module for registering user analytics."""

import datetime
import hashlib
import json
import logging
import os
import uuid
from enum import Enum

import asset_utilities as asu
import get_token
import jsonschema
import session_utilities as su
from google.cloud import bigquery

logger = logging.getLogger(__name__)

_INACTIVITY_TIMEOUT = {"hours": 8}


SCHEMA = {
    "type": "object",
    "properties": {
        "visit_id": {"type": ["string", "null"], "minLength": 32, "maxLength": 32},
        "session_id": {"type": ["string", "null"], "minLength": 32, "maxLength": 32},
        "user_hash": {"type": ["string", "null"], "minLength": 32, "maxLength": 32},
        "action": {"type": "integer", "minimum": 0, "maximum": 5},
        "timestamp": {"type": "integer", "minimum": 1672435955},
        "action_data": {
            "type": "object",
            "properties": {
                "current_page": {"type": "string"},
                "current_tab": {"type": "integer", "minimum": 0, "maximum": 4},
                "service": {"type": "string"},
                "targets": {"type": "array"},
            },
            "additionalProperties": False,
        },
    },
    "additionalProperties": False,
    "required": [
        "visit_id",
        "session_id",
        "user_hash",
        "action",
        "timestamp",
        "action_data",
    ],
}


class ACTIONS(Enum):
    """Actions that a user can take that are logged in the Analytics database."""

    FRONTEND = 0
    SET_ACTIVE_PAGE = 1
    SET_ACTIVE_TUTORIAL_TAB = 2
    UPDATE_STATUS = 3
    ASSET_STATUS = 4
    ASSET_UPDATE = 5


def update_visit_cookie(request, response):
    """Update the visit_id cookie to a new expire time."""
    visit_id = request.cookies.get("visit_id", uuid.uuid4().hex)
    response.set_cookie(
        "visit_id",
        value=visit_id,
        secure=True,
        httponly=True,
        domain=su.user_service_domain(request),
        expires=datetime.datetime.now() + datetime.timedelta(**_INACTIVITY_TIMEOUT),
    )
    return response


def validate_data(instance):
    """Validate data, with logging if there is a problem."""
    try:
        jsonschema.validate(instance=instance, schema=SCHEMA)
        instance["action_data"] = json.dumps(instance["action_data"])
    except jsonschema.exceptions.ValidationError as exc:
        logging.error("Validation error: %s", exc)


def register_action(request, response, action, data=None):
    """Register a user action with the analytics database."""
    target_database = "prod" if su.is_prod() else "dev"
    if data is None:
        data = {}

    session_id = request.cookies.get("session_id")
    if session_id:
        tok_response = get_token.get_token(request, token_type="email")
        if "response" in tok_response:
            logging.error(
                "Error retriving user information: %s", tok_response["response"]
            )
            response.delete_cookie("session_id", domain=su.user_service_domain(request))
            response.delete_cookie(
                "user_logged_in", domain=su.user_service_domain(request)
            )
            user_hash = None
        else:
            user_hash = hashlib.md5(tok_response["email"].encode("utf-8")).hexdigest()
    else:
        user_hash = None
    instance = {
        "visit_id": request.cookies.get("visit_id"),
        "session_id": session_id,
        "user_hash": user_hash,
        "action": action.value,
        "timestamp": int(datetime.datetime.now().timestamp()),
        "action_data": data,
    }
    validate_data(instance)

    client = bigquery.Client(credentials=asu.get_credentials())
    table = client.get_table(
        client.dataset(os.environ["ANALYTICS_DATABASE"]).table(target_database)
    )
    insert_response = client.insert_rows_json(json_rows=[instance], table=table)
    if insert_response:
        logging.error("Error inserting into analytics database: %s", insert_response)

    update_visit_cookie(request, response)
    return response
