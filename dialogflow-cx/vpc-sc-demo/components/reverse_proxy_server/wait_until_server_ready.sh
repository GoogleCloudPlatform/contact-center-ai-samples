#!/usr/bin/env bash

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
 