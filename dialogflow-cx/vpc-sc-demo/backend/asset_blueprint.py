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

"""Blueprint for checking status of assets in project under terraform management."""

import json
import logging
import tempfile

import asset_utilities as au
import flask
import get_token
from invoke import context

asset = flask.Blueprint("asset", __name__)
logger = logging.getLogger(__name__)


ACCESS_POLICY_RESOURCE = (
    "module.service_perimeter."
    "google_access_context_manager_access_policy.access_policy[0]"
)


@asset.route("/asset_status", methods=["GET"])
def asset_status():  # pylint: disable=too-many-locals
    """Get status of terraform-tracked assets."""
    debug = flask.request.args.get("debug") == "true"
    target = flask.request.args.get("target", None)
    update = flask.request.args.get("update", True)
    token_dict = get_token.get_token(flask.request, token_type="access_token")
    if "response" in token_dict:
        return token_dict["response"]
    access_token = token_dict["access_token"]
    env = au.get_terraform_env(access_token, flask.request.args, debug=debug)
    ctx = context.Context()
    module = "/deploy/terraform/main.tf"
    prefix = f'terraform/{flask.request.args["project_id"]}'
    with tempfile.TemporaryDirectory() as workdir:

        result = au.tf_init(ctx, module, workdir, env, prefix)

        if result:
            return result

        resource_id_dict = {}
        if update:
            result = au.tf_plan(ctx, module, workdir, env, target=target)
            if result is not None:
                if "response" in result:
                    return result["response"]
                for hook in result["hooks"]["refresh_complete"]:
                    if "id_value" in hook:
                        resource_id_dict[hook["resource"]["addr"]] = hook["id_value"]

        if ACCESS_POLICY_RESOURCE in resource_id_dict:
            access_policy_id = resource_id_dict[ACCESS_POLICY_RESOURCE]
            response = au.get_access_policy_title(access_token, access_policy_id)
            if "response" in response:
                return response["response"]
            access_policy_title = response["access_policy_title"]
        else:
            access_policy_title = None

        result = au.tf_state_list(ctx, module, workdir, env)
        if "response" in result:
            return result["response"]
        resources = result["resources"]

        return flask.Response(
            status=200,
            response=json.dumps(
                {
                    "status": "OK",
                    "resources": resources,
                    "resource_id_dict": resource_id_dict,
                    "accessPolicyTitle": access_policy_title,
                }
            ),
        )
