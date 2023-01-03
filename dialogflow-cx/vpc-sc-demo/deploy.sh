#!/usr/bin/env bash
# Copyright 2023 Google LLC
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

SHORT=t::,h
LONG=tag::,help
OPTS=$(getopt -a -n weather --options $SHORT --longoptions $LONG -- "$@")

help()
{
    echo "Usage: deploy [ -t | --tag ]
              [ -h | --help  ]"

    exit 2
}

VALID_ARGUMENTS=$# # Returns the count of arguments that are in short or long options

if [ "$VALID_ARGUMENTS" -eq 0 ]; then
  help
fi

eval set -- "$OPTS"

while :
do
  case "$1" in
    -t | --tag )
      SERVICE_TAG="$2"
      shift 2
      ;;
    -h | --help)
      help
      ;;
    --)
      shift;
      break
      ;;
    *)
      echo "Unexpected option: $1"
      help
      ;;
  esac
done

SERVICE_NAME="vpc-sc-live-demo"
IMAGE="gcr.io/${PROJECT_ID?}/${SERVICE_NAME?}"
TAG='latest'

sudo docker build -t "${IMAGE?}":"${TAG?}" .
sudo docker push "${IMAGE?}":"${TAG?}"
gcloud run deploy "${SERVICE_NAME?}"\
  --project="${PROJECT_ID?}"\
  --platform=managed\
  --region=us-central1\
  --image="${IMAGE?}":"${TAG?}"\
  --allow-unauthenticated \
  --tag="${SERVICE_TAG?}"
