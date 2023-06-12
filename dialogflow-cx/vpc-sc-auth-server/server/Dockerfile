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


# Start by pulling the python image
FROM gcr.io/google.com/cloudsdktool/google-cloud-cli:alpine
RUN apk add --no-cache bash==5.1.16-r0 py3-pip==20.3.4-r1 build-base==0.5-r3 python3-dev==3.9.15-r0

# Copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

# Switch working directory
WORKDIR /app

# Install the dependencies and packages in the requirements file
RUN pip install --no-cache-dir --upgrade pip==22.3.1 && pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

# Copy every content from the local file to the image
COPY app.py /app/app.py
COPY ./session.py /app/session.py
COPY ./utilities.py /app/utilities.py
COPY ./aes_cipher.py /app/aes_cipher.py

CMD ["gunicorn", "--bind=0.0.0.0:5000", "--workers=1", "--threads=8", "--log-level=info", "app:app"]
