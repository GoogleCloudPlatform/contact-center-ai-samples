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

# Settings
export BASE_TERRAFORM_IMAGE="hashicorp/terraform:1.3.6"
export TERRAFORM_IMAGE="terraform_deploy_test:latest"

# Build a test runner image:
sudo docker build --build-arg BASE_IMAGE="${BASE_TERRAFORM_IMAGE?}" -t ${TERRAFORM_IMAGE?} .

sudo docker run --rm ${TERRAFORM_IMAGE?}