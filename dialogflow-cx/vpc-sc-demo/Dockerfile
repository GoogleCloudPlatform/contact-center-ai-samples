# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM gcr.io/google.com/cloudsdktool/google-cloud-cli:alpine
RUN apk add --no-cache \
  bash==5.1.16-r0 \
  py3-pip==20.3.4-r1 \
  build-base==0.5-r3 \
  python3-dev==3.9.16-r0 \
  nodejs==16.17.1-r0 \
  npm==8.1.3-r0 \
  jq==1.6-r1 \
  openssl==1.1.1s-r1

ARG PROD
ENV PROD=${PROD:-true}

RUN wget -nv https://releases.hashicorp.com/terraform/1.2.9/terraform_1.2.9_linux_amd64.zip
RUN unzip terraform_1.2.9_linux_amd64.zip
RUN mv terraform /usr/bin/terraform

# Frontend
WORKDIR /app/frontend

COPY frontend/ /app/frontend/
RUN npm install react-scripts@5.0.1 && npm run build

# Backend
WORKDIR /app

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip==22.3.1
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/create_keys.py /app/create_keys.py
RUN python3 create_keys.py

COPY backend/app.py /app/app.py
COPY backend/tasks.py /app/tasks.py
COPY backend/demo-server-key.json /app/demo-server-key.json

RUN mkdir -p /app/.terraform.d/plugin-cache
COPY components /app/components

EXPOSE 8080
CMD ["gunicorn", "--bind=0.0.0.0:8080", "--workers=1", "--threads=8", "--log-level=info", "app:app"]
