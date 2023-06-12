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

SHORT=z::,p::,t::,h
LONG=zone::,project_id::,token::,help
OPTS=$(getopt -a --options $SHORT --longoptions $LONG -- "$@")

help()
{
    echo "Usage: deploy_agent [ -z | --zone   ]
                    [ -p | --project_id   ]
                    [ -t | --token ]
                    [ -h | --help         ]"
    exit 2
}

VALID_ARGUMENTS=$#

if [ "$VALID_ARGUMENTS" -eq 0 ]; then
  help
fi

eval set -- "$OPTS"

while :
do
  case "$1" in
    -z | --zone )
      ZONE="$2"
      shift 2
      ;;
    -p | --project_id )
      PROJECT_ID="$2"
      shift 2
      ;;
    -t | --token )
      TOKEN="$2"
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

export CLOUDSDK_AUTH_ACCESS_TOKEN=${TOKEN?}
gcloud config set project "${PROJECT_ID?}"

READY=false
until [ ${READY?} = true ]
do
  if gcloud compute instances get-serial-port-output --start=0 webhook-server --zone "${ZONE?}" | grep -q "google-startup-scripts.service: Succeeded"; then
    READY=true
  fi
  sleep 1
done
 