#!/usr/bin/env sh
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

SHORT=r::,p::,w::,t::,h
LONG=region::,project_id::,webhook_name::,token::,help
OPTS=$(getopt -a --options $SHORT --longoptions $LONG -- "$@")

help()
{
    echo "Usage: deploy_agent [ -r | --region     ]
                    [ -p | --project_id   ]
                    [ -w | --webhook_name ]
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
    -r | --region )
      REGION="$2"
      shift 2
      ;;
    -p | --project_id )
      PROJECT_ID="$2"
      shift 2
      ;;
    -w | --webhook_name )
      WEBHOOK_NAME="$2"
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

WEBHOOK_TRIGGER_URI="https://${REGION?}-${PROJECT_ID?}.cloudfunctions.net/${WEBHOOK_NAME?}"

echo 'Getting agent name...'
AGENT_FULL_NAME=$(curl -s -X GET -H "Authorization: Bearer ${TOKEN?}" \
  -H "Content-Type:application/json" \
  -H "x-goog-user-project: ${PROJECT_ID?}" \
  "https://${REGION?}-dialogflow.googleapis.com/v3/projects/${PROJECT_ID?}/locations/${REGION?}/agents" | jq -r '.agents[0].name')
echo '  Done getting agent name.'

echo 'Restoring agent...'
curl -s -X POST \
  -H "Authorization: Bearer ${TOKEN?}" \
  -H "Content-Type:application/json" \
  -H "x-goog-user-project: ${PROJECT_ID?}" \
  -d \
  '{
    "agentUri": "gs://gassets-api-ai/prebuilt_agents/cx-prebuilt-agents/exported_agent_Telecommunications.blob"
  }' \
  "https://${REGION?}-dialogflow.googleapis.com/v3/${AGENT_FULL_NAME?}:restore"
sleep 5
echo '  Done restoring agent.'

echo 'Getting webhook name...'
WEBHOOK_FULL_NAME=$(curl -s -X GET \
  -H "Authorization: Bearer ${TOKEN?}" \
  -H "x-goog-user-project: ${PROJECT_ID?}" \
  "https://${REGION?}-dialogflow.googleapis.com/v3/${AGENT_FULL_NAME?}/webhooks" | jq -r '.webhooks[0].name')
echo '  Done getting webhook name.'

echo 'Setting webhook fulfillment to Cloud Function...'
curl -s -X PATCH \
  -H "Authorization: Bearer ${TOKEN?}" \
  -H "Content-Type:application/json" \
  -H "x-goog-user-project: ${PROJECT_ID?}" \
  -d \
  "{
    \"displayName\": \"cxPrebuiltAgentsTelecom\",
    \"genericWebService\": {\"uri\": \"${WEBHOOK_TRIGGER_URI?}\"}
  }" \
  "https://${REGION?}-dialogflow.googleapis.com/v3/${WEBHOOK_FULL_NAME?}"
echo '  Done setting webhook fulfillment to Cloud Function.'