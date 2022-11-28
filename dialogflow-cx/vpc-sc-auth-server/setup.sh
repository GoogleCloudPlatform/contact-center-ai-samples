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

source config.env

gcloud --quiet auth login "${PRINCIPAL?}" --no-launch-browser
gcloud config set project "${PROJECT_ID?}"

gsutil mb gs://"${PROJECT_BUCKET?}"
gsutil retention set 1d gs://"${PROJECT_BUCKET?}"
gcloud auth configure-docker "${REGION?}-docker.pkg.dev"
gcloud artifacts repositories create "${ARTIFACT_REGISTRY?}" --location "${REGION?}" --repository-format "docker"
gcloud secrets create application-client-secret --replication-policy="automatic"
gcloud secrets versions add application-client-secret --data-file="application-client-secret"

gcloud projects add-iam-policy-binding "${PROJECT_ID?}" \
  --member=serviceAccount:"${PROJECT_NUMBER?}"-compute@developer.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor