#!/usr/bin/env bash
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

source config.env

if [[ $(git diff --stat) != '' ]]; then 
  echo 'Deployment cancelled: dirty repository' 
  exit 0
fi

gcloud --quiet auth login "${PRINCIPAL?}" --no-launch-browser
gcloud config set project "${PROJECT_ID?}"

# Revision in Cloud Run tagged with current repo hash
REVISION_SUFFIX="$(git rev-parse --short HEAD)"
SERVICE_NAME="authentication-service"
gcloud builds submit server --tag="${IMAGE_URI?}" --gcs-log-dir=gs://"${PROJECT_ID?}"
gcloud run deploy "${SERVICE_NAME?}" \
  --allow-unauthenticated \
  --image "${IMAGE_URI?}" \
  --platform managed \
  --region "${REGION?}" \
  --port=5000 \
  --ingress=all \
  --set-env-vars=CLIENT_ID="${CLIENT_ID?}",SESSION_BUCKET="${SESSION_BUCKET?}",IP_ADDRESS="${DOMAIN?}",PROD=true \
  --tag="${SERVICE_TAG?}" \
  --revision-suffix="${REVISION_SUFFIX?}"
gcloud run services update-traffic ${SERVICE_NAME?} \
  --update-tags="r-${REVISION_SUFFIX?}=${SERVICE_NAME?}-${REVISION_SUFFIX?}"
