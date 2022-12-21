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
sudo apt-get install -y openssl

mkdir -p /etc/docker/mount
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


BUCKET=$(curl http://metadata.google.internal/computeMetadata/v1/instance/attributes/bucket -H "Metadata-Flavor: Google")
IMAGE=$(curl http://metadata.google.internal/computeMetadata/v1/instance/attributes/image -H "Metadata-Flavor: Google")
BOT_USER=$(curl http://metadata.google.internal/computeMetadata/v1/instance/attributes/bot_user -H "Metadata-Flavor: Google")
WEBHOOK_TRIGGER_URI=$(curl http://metadata.google.internal/computeMetadata/v1/instance/attributes/webhook_trigger_uri -H "Metadata-Flavor: Google")

mkdir -p /etc/docker/mount/ssl
ssl_key=/etc/docker/mount/ssl/server.key
ssl_csr=/etc/docker/mount/ssl/server.csr
ssl_crt=/etc/docker/mount/ssl/server.crt
ssl_der=/etc/docker/mount/ssl/server.der
openssl genrsa -out ${ssl_key} 2048
openssl req -nodes -new -sha256 -key ${ssl_key} -subj "/CN=webhook.internal" -out ${ssl_csr}
openssl x509 -req -days 3650 -in ${ssl_csr} -signkey ${ssl_key} -out ${ssl_crt} -extfile <(printf "\nsubjectAltName='DNS:webhook.internal'")
openssl x509 -in ${ssl_crt} -out ${ssl_der} -outform DER
gsutil cp ${ssl_der} gs://"${BUCKET?}"/server.der

echo \
'
version: "3.9"
services:
  app:
    image: '"${IMAGE?}"'
    environment:
     - BOT_USER='"${BOT_USER?}"'
     - WEBHOOK_TRIGGER_URI='"${WEBHOOK_TRIGGER_URI?}"'
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
