#! /bin/bash
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

sudo apt-get update
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    jq \
    lsb-release
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

mkdir /etc/docker/mount
echo \
'server { 
    server_name             webhook.internal;
    listen                  443 ssl;
    listen                  [::]:443 ssl;
    ssl_certificate         /root/ssl/server.crt;
    ssl_certificate_key     /root/ssl/server.key;
    ssl_protocols TLSv1.2;
    ssl_verify_depth 2;
    error_log /var/log/nginx/proxy_error.log debug;
    location / {
        proxy_pass "http://app:8080";
    }
    error_page   500 502 503 504  /50x.html;
}' | sudo tee /etc/docker/mount/nginx.conf

mkdir /etc/docker/mount/ssl
gsutil cp gs://vpc-sc-demo-nicholascain14/ssl/server.crt /etc/docker/mount/ssl/server.crt
gsutil cp gs://vpc-sc-demo-nicholascain14/ssl/server.key /etc/docker/mount/ssl/server.key

echo \
'
version: "3.9"
services:
  app:
    image: us-central1-docker.pkg.dev/vpc-sc-demo-nicholascain14/webhook-registry/webhook-server-image:latest
  nginx:
    image: nginx
    volumes:
      - ./mount/nginx.conf:/etc/nginx/conf.d/default.conf
      - ./mount/ssl/server.key:/root/ssl/server.key
      - ./mount/ssl/server.crt:/root/ssl/server.crt
    ports:
      - "443:443"
    depends_on:
      - app
' | sudo tee /etc/docker/docker-compose.yaml
sudo gcloud --quiet auth configure-docker us-central1-docker.pkg.dev
cd /etc/docker && sudo docker compose up -d

echo '{"fulfillmentInfo":{"tag":"validatePhoneLine"},"sessionInfo":{"parameters":{"phone_number":"123456"}}}' | sudo tee /etc/docker/ping-payload.json