# Copyright 2023 Google LLC
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

ARG BASE_IMAGE
# hadolint ignore=DL3006
FROM ${BASE_IMAGE}

RUN apk add --no-cache\
  python3==3.10.9-r1\
  py3-pip==22.3.1-r1\
  graphviz==7.0.5-r0\
  gcc==12.2.1_git20220924-r4\
  python3-dev==3.10.9-r1\
  graphviz-dev==7.0.5-r0\
  musl-dev==1.2.3-r4

COPY ./ /terraform
WORKDIR /terraform

RUN pip install --no-cache-dir --upgrade pip==22.3.1 && pip install --no-cache-dir -r tests/requirements.txt
RUN terraform init
RUN terraform graph -type plan
RUN terraform graph -type plan > dependencies.dot

ENTRYPOINT ["pytest"]
