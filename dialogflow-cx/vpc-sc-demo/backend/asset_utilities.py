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
# pylint: disable=inconsistent-return-statements

"""Utility Module to set and remove terraform assets."""

import json
import logging
import os
import re
import shlex

import flask
import google.auth.transport.requests
import requests
import status_utilities as su
from flask import Response
from google.oauth2 import service_account
from invoke import task

logger = logging.getLogger(__name__)


RESOURCE_GROUP = {
    "module.service_directory": {
        "module.service_directory.google_service_directory_endpoint.reverse_proxy",
        "module.service_directory.google_service_directory_namespace.reverse_proxy",
        "module.service_directory.google_service_directory_service.reverse_proxy",
        (
            "module.service_perimeter.google_access_context_manager_service_perimeter"
            ".service_perimeter[0]"
        ),
    },
    "module.services": {
        "module.services.google_project_service.appengine",
        "google_project_service.artifactregistry",
        "module.services.google_project_service.run",
        "module.services.google_project_service.vpcaccess",
        "google_project_service.accesscontextmanager",
        "google_project_service.cloudbilling",
        "google_project_service.cloudbuild",
        "google_project_service.cloudfunctions",
        "google_project_service.compute",
        "google_project_service.dialogflow",
        "google_project_service.iam",
        "google_project_service.servicedirectory",
    },
    "module.vpc_network": {
        "module.vpc_network.google_artifact_registry_repository.webhook_registry",
        "module.vpc_network.google_cloudbuild_trigger.reverse_proxy_server",
        "module.vpc_network.google_compute_address.reverse_proxy_address",
        "module.vpc_network.google_compute_firewall.allow",
        "module.vpc_network.google_compute_firewall.allow_dialogflow",
        "module.vpc_network.google_compute_instance.reverse_proxy_server",
        "module.vpc_network.google_compute_network.vpc_network",
        "module.vpc_network.google_compute_router.nat_router",
        "module.vpc_network.google_compute_router_nat.nat_manual",
        "module.vpc_network.google_compute_subnetwork.reverse_proxy_subnetwork",
        "module.vpc_network.google_project_iam_member.dfsa_sd_pscAuthorizedService",
        "module.vpc_network.google_project_iam_member.dfsa_sd_viewer",
        "module.vpc_network.google_project_service_identity.dfsa",
        "module.vpc_network.google_pubsub_topic.reverse_proxy_server_build",
        "module.vpc_network.google_storage_bucket_object.proxy_server_source",
    },
    "module.webhook_agent": {
        "module.webhook_agent.google_cloudfunctions_function.webhook",
        "google_storage_bucket.bucket",
        "module.webhook_agent.google_storage_bucket_object.webhook",
        "module.webhook_agent.google_dialogflow_cx_agent.full_agent",
    },
    "all": {
        "module.webhook_agent",
        "module.vpc_network",
        "module.services",
        "module.service_directory",
    },
}

PREFIX_PATTERN = re.compile(r"^terraform/[a-z][a-z0-9-]{4,28}[a-z0-9]$")
VALID_TARGETS = frozenset(RESOURCE_GROUP.keys()).union(*RESOURCE_GROUP.values())


def is_valid_target(target):
    """Return True if target is an allowlisted Terraform resource or module."""
    return isinstance(target, str) and target in VALID_TARGETS


def get_credentials():
    """Helper function to get service account credentials."""
    return service_account.Credentials.from_service_account_file(
        "/backend/demo-server-key.json",
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )


def get_access_policy_title(token, access_policy_id):
    """Get access_policy_title using the accesscontextmanager API."""
    headers = {}
    headers["Authorization"] = f"Bearer {token}"
    result = requests.get(
        f"https://accesscontextmanager.googleapis.com/v1/accessPolicies/{access_policy_id}",
        headers=headers,
        timeout=10,
    )
    if result.status_code != 200:
        # Should this return the status from the result.status_code?
        return {"response": flask.Response(status=500, response=result.text)}
    return {"access_policy_title": result.json()["title"]}


def get_terraform_env(access_token, request_args, debug=False):
    """Build an dictionary of environment variables for terraform run."""
    env = {}
    env["GOOGLE_OAUTH_ACCESS_TOKEN"] = access_token
    env["TF_VAR_project_id"] = request_args["project_id"]
    env["TF_VAR_bucket"] = request_args["bucket"]
    env["TF_VAR_region"] = request_args["region"]
    if request_args.get("access_policy_title", None):
        response = su.get_access_policy_name(
            access_token,
            request_args["access_policy_title"],
            request_args["project_id"],
            error_code=500,
        )
        if "response" in response:
            return response
        env["TF_VAR_access_policy_name"] = response["access_policy_name"]
    else:
        env["TF_VAR_access_policy_name"] = "null"
    if debug:
        env["TF_LOG"] = "DEBUG"
    return env


@task
def tf_init(context, module, workdir, env, prefix):
    """Initialize terraform."""
    if not isinstance(prefix, str) or not PREFIX_PATTERN.fullmatch(prefix):
        return Response(
            status=400,
            response=json.dumps({"status": "BLOCKED", "reason": "INVALID_PREFIX"}),
        )
    user_access_token = env.pop("GOOGLE_OAUTH_ACCESS_TOKEN")
    debug = "TF_LOG" in env

    credentials = get_credentials()
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    env["GOOGLE_OAUTH_ACCESS_TOKEN"] = credentials.token
    access_token_cfg = shlex.quote(f'access_token={env["GOOGLE_OAUTH_ACCESS_TOKEN"]}')
    bucket_cfg = shlex.quote(f'bucket={os.environ["TF_PLAN_STORAGE_BUCKET"]}')
    prefix_cfg = shlex.quote(f"prefix={prefix}")
    promise = context.run(
        (
            f"cp {shlex.quote(module)} {shlex.quote(workdir)} && "
            f"terraform -chdir={shlex.quote(workdir)} init "
            "-upgrade -reconfigure "
            f"-backend-config={access_token_cfg} "
            f"-backend-config={bucket_cfg} "
            f"-backend-config={prefix_cfg}"
        ),
        warn=True,
        hide=True,
        asynchronous=True,
    )
    result = promise.join()
    env["GOOGLE_OAUTH_ACCESS_TOKEN"] = user_access_token

    if debug:
        logging.debug(result.exited)
        logging.debug(result.stdout)
        logging.debug(result.stderr)

    if result.exited:
        return Response(
            status=500,
            response=json.dumps(
                {
                    "status": "ERROR",
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                }
            ),
        )


@task
def tf_plan(context, module, workdir, env, target=None):
    """Create terraform plan."""
    if target is not None and not is_valid_target(target):
        return {
            "response": Response(
                status=400,
                response=json.dumps({"status": "BLOCKED", "reason": "INVALID_TARGET"}),
            )
        }
    debug = "TF_LOG" in env
    target_option = f"-target={shlex.quote(target)}" if target else ""
    json_option = "-json" if not debug else ""
    promise = context.run(
        (
            f"cp {shlex.quote(module)} {shlex.quote(workdir)} && "
            f"terraform -chdir={shlex.quote(workdir)} plan {json_option} "
            "-refresh-only -var "
            f'{shlex.quote("access_token=" + env["GOOGLE_OAUTH_ACCESS_TOKEN"])} '
            f"{target_option}"
        ),
        warn=True,
        hide=True,
        asynchronous=True,
        env=env,
    )
    result = promise.join()

    if debug:
        logging.debug(result.exited)
        logging.debug(result.stdout)
        logging.debug(result.stderr)
    else:
        errors = []
        hooks = {
            "refresh_start": [],
            "refresh_complete": [],
            "apply_complete": [],
            "apply_start": [],
        }
        lines = result.stdout.split("\n")
        for line in lines:
            if line.strip():
                try:
                    message = json.loads(line.strip())
                    if message["@level"] == "error":
                        errors.append(message)
                    if "hook" in message:
                        hooks[message["type"]].append(message["hook"])
                except KeyError:
                    logging.debug("COULD NOT LOAD: %s", line)
        if errors:
            return {
                "response": Response(
                    status=500,
                    response=json.dumps(
                        {
                            "status": "ERROR",
                            "errors": errors,
                        }
                    ),
                )
            }
        return {"hooks": hooks}


@task
def tf_apply(  # pylint: disable=too-many-arguments,too-many-locals
    context,
    module,
    workdir,
    env,
    destroy,
    target=None,
    verbose=False,
):
    """Apply terraform plan."""
    if target is not None and not is_valid_target(target):
        return Response(
            status=400,
            response=json.dumps({"status": "BLOCKED", "reason": "INVALID_TARGET"}),
        )
    debug = "TF_LOG" in env
    target_option = f"-target={shlex.quote(target)}" if target else ""
    json_option = "-json" if not debug else ""
    destroy_option = "--destroy" if destroy else ""
    verbose_option = 'export TF_LOG="DEBUG" && ' if verbose else ""
    access_token_var = shlex.quote(f'access_token={env["GOOGLE_OAUTH_ACCESS_TOKEN"]}')

    promise = context.run(
        f"cp {shlex.quote(module)} {shlex.quote(workdir)} && "
        f"{verbose_option}"
        f"terraform -chdir={shlex.quote(workdir)} apply -lock-timeout=10s {json_option}"
        f" --auto-approve -var {access_token_var} "
        f"{destroy_option} {target_option}",
        warn=True,
        hide=None,
        asynchronous=True,
        env=env,
    )
    result = promise.join()
    if debug:
        logging.debug(result.exited)
        logging.debug(result.stdout)
        logging.debug(result.stderr)
    else:
        errors = []
        lines = result.stdout.split("\n")
        for line in lines:
            if line.strip():
                try:
                    message = json.loads(line)
                    if message["@level"] == "error":
                        errors.append(message)
                except json.decoder.JSONDecodeError:
                    logging.debug("COULD NOT LOAD: %s", line)
        if errors:
            # Should return dict to match the other function...
            return Response(
                status=500,
                response=json.dumps(
                    {
                        "status": "ERROR",
                        "errors": errors,
                    }
                ),
            )


@task
def tf_state_list(context, module, workdir, env):
    """Get list of all states."""
    debug = "TF_LOG" in env
    promise = context.run(
        f"cp {shlex.quote(module)} {shlex.quote(workdir)} && "
        f"terraform -chdir={shlex.quote(workdir)} state list",
        warn=True,
        hide=True,
        asynchronous=True,
        env=env,
    )
    result = promise.join()

    if debug:
        logging.debug(result.exited)
        logging.debug(result.stdout)
        logging.debug(result.stderr)

    if result.exited:
        return {
            "response": Response(
                status=500,
                response=json.dumps(
                    {
                        "status": "ERROR",
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                    }
                ),
            )
        }
    status_dict = {"resources": result.stdout.split()}
    for group_name, group_resources in RESOURCE_GROUP.items():
        if group_resources.issubset(set(status_dict["resources"])):
            status_dict["resources"].append(group_name)
    logging.debug(status_dict["resources"])
    return status_dict


def get_debug(request):
    """Get boolean to engage debug mode for terraform"""
    if (request.args.get("debug") == "true") or (logging.DEBUG >= logging.root.level):
        return True
    return False


def validate_project_id(project_id, access_token):
    """Confirm if the current project_id is valid for current user."""
    if not su.is_valid_project_id(project_id):
        return flask.Response(
            status=500,
            response=json.dumps({"status": "BLOCKED", "reason": "UNKNOWN_PROJECT_ID"}),
        )
    headers = {}
    headers["Authorization"] = f"Bearer {access_token}"
    response = requests.get(
        f"https://cloudresourcemanager.googleapis.com/v1/projects/{project_id}",
        headers=headers,
        timeout=10,
    )
    if response.status_code != 200:
        return flask.Response(
            status=500,
            response=json.dumps({"status": "BLOCKED", "reason": "UNKNOWN_PROJECT_ID"}),
        )
