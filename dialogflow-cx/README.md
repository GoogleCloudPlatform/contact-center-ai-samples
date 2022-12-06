<!-- 
Copyright 2022 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License. 
-->

# Dialogflow CX Webhook Python Sample

This project uses [Google Cloud Functions](https://cloud.google.com/functions)
to create a webhook for a
[Dialogflow CX](https://cloud.google.com/dialogflow/cx/docs) agent.

## Setup

### Install dependencies

1. Install pyenv: <https://github.com/pyenv/pyenv#installation>
1. Use pyenv to install
    [the latest version of Python 3](https://www.python.org/downloads/) for
    example, to install Python version 3.10.1, run: `pyenv install 3.10.1`
1. Create a Python virtual environment with the installed version of Python 3,
    for example, to create a Python 3.10.1 virtual environment called
    `dialogflow-webhook`, run: `pyenv virtualenv 3.10.1 dialogflow-webhook`
1. Clone this repository and `cd` to the root of the repository
1. Configure pyenv to use the virtual python environment we created earlier when
    in this repository: `pyenv local dialogflow-webhook`
1. Install the prerequisites: `pip install -r requirements.txt`

### Setup Google Cloud

1. Install the Cloud SDK: <https://cloud.google.com/sdk/docs/install>
1. Run `gcloud init`, to
    [create a new project](https://cloud.google.com/resource-manager/docs/creating-managing-projects#creating_a_project),
    and
    [link a billing to your project](https://cloud.google.com/sdk/gcloud/reference/billing)
1. Enable the Document AI API: `gcloud services enable
   dialogflow.googleapis.com cloudfunctions.googleapis.com`
1. Setup application default authentication, run: `gcloud auth
   application-default login`
1. Clone this repository and enter the folder containing the sample code:

   ```bash
   git clone https://github.com/GoogleCloudPlatform/contact-center-ai-samples.git
   cd contact-center-ai-samples/dialogflow-cx
   ```

1. Deploy the Cloud Function:
   Here `<REGION>` is the Google Cloud region of your function and
   `<PROJECT_ID>` is the Google Cloud project ID that contains your Cloud
   Function.

   ```bash
   gcloud functions deploy dialogflow_webhook \
     --runtime python39 \
     --project=${PROJECT_ID?} \
     --region=${REGION?} \
     --source=webhook \
     --entry-point=webhook_fcn \
     --trigger-http \
     --allow-unauthenticated
   ```

1. Run the sample:

   ```bash
   python main.py --webhook-url ${CLOUD_FUNCTION_URL?}
   ```

   where `<CLOUD_FUNCTION_URL>` is the URL of the Cloud Function you deployed
   in the previous step. The URL should take the following form:

   ```bash
   CLOUD_FUNCTION_URL="https://${REGION?}-${PROJECT_ID?}.cloudfunctions.net/webhook_fcn"
   ```

   For example:

   ```bash
   https://us-central1-my-project-id.cloudfunctions.net/webhook_fcn
   ```

## Running the sample

1. Run a Dialog flow agent sample:

```bash
python basic_webhook_sample.py \
  --webhook-uri=${CLOUD_FUNCTION_URL?} \
  --project-id=${PROJECT_ID?} \
  --agent-display-name=example_agent
```
