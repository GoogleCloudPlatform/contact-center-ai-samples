#!/bin/bash
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
set -e


# Settings (Required):
export PROJECT_ID= # Fill in an existing project_id, with enabled billing info
export PRINCIPAL= # Fill in an existing account with sufficient IAM permissions to deploy
export TF_PLAN_STORAGE_BUCKET= # Fill in an existing bucket name

# Settings (Defaults):
export TERRAFORM_IMAGE="hashicorp/terraform:1.3.6"
export PREFIX="terraform/${PROJECT_ID?}/webhook"

# Initialize:
gcloud --quiet auth login "${PRINCIPAL?}" --no-launch-browser
gcloud config set project "${PROJECT_ID?}"
gcloud services enable cloudresourcemanager.googleapis.com


sudo docker run -w /app -v "$(pwd)":/app "${TERRAFORM_IMAGE?}" init -upgrade -reconfigure -backend-config="access_token=$(gcloud auth print-access-token)" -backend-config="bucket=${TF_PLAN_STORAGE_BUCKET?}" -backend-config="prefix=${PREFIX?}"

sudo docker run -w /app -v "$(pwd)":/app -e GOOGLE_OAUTH_ACCESS_TOKEN="$(gcloud auth print-access-token)" "${TERRAFORM_IMAGE?}" apply --auto-approve -var project_id="${PROJECT_ID?}" -var bucket="${TF_PLAN_STORAGE_BUCKET?}"
