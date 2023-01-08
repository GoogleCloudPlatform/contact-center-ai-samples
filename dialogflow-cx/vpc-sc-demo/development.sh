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

source config.env

export USER_SERVICE_IMAGE='vpc-sc-demo'
export USER_SERVICE_TAG_BASE='development'

sudo docker build --build-arg PROD=false -t ${USER_SERVICE_IMAGE?}:${USER_SERVICE_TAG_BASE?} .

sudo docker run -it \
  -p 8081:8081 \
  --rm \
  --env PROD=false \
  --env FLASK_DEBUG=1 \
  --env ANALYTICS_DATABASE="${ANALYTICS_DATABASE?}" \
  --env TF_PLAN_STORAGE_BUCKET="${TF_PLAN_STORAGE_BUCKET?}" \
  -v "$(pwd)"/backend:/backend \
  -v "$(pwd)"/deploy:/deploy \
  -v "$(pwd)"/components/webhook/telecom-webhook-src:/components/telecom-webhook-src \
  -v "$(pwd)"/components/reverse_proxy_server/proxy-server-src:/components/proxy-server-src \
  ${USER_SERVICE_IMAGE?}:${USER_SERVICE_TAG_BASE?} \
  flask run --port 8081 --host=0.0.0.0
