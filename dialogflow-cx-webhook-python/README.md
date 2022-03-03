# Dialogflow CX Webhook Python Sample

This project uses [Google Cloud Functions](https://cloud.google.com/functions)
to create a webhook for a
[Dialogflow CX](https://cloud.google.com/dialogflow/cx/docs) agent.

## Setup

### Install dependencies

1. Install pyenv: https://github.com/pyenv/pyenv#installation
1. Use pyenv to install
    [the latest version of Python 3](https://www.python.org/downloads/) for
    example, to install Python version 3.10.1, run: `pyenv install 3.10.1`
1. Create a Python virtual environment with the installed version of Python 3,
    for example, to create a Python 3.10.1 virtual environment called
    `dialogflow-webhook`, run: `pyenv virtualenv 3.10.1 dialogflow-webhook`
1. Clone this repo and `cd` to the root of the repo
1. Configure pyenv to use the virtual python environment we created earlier when
    in this repo: `pyenv local dialogflow-webhook`
1. Install the prerequisites: `pip install -r requirements.txt`

### Setup Google Cloud

1. Install the Cloud SDK: https://cloud.google.com/sdk/docs/install
1. Run `gcloud init`, to
    [create a new project](https://cloud.google.com/resource-manager/docs/creating-managing-projects#creating_a_project),
    and
    [link a billing to your project](https://cloud.google.com/sdk/gcloud/reference/billing)
1. Enable the Document AI API: `gcloud services enable
   dialogflow.googleapis.com cloudfunctions.googleapis.com`
1. Setup application default authentication, run: `gcloud auth
   application-default login`
1. Deploy the Cloud Function:
   ```
   gcloud functions deploy dialogflow_webhook \
     --runtime python39 \
     --trigger-http \
     --allow-unauthenticated
   ```
   and make a note of the `url` of `httpsTrigger` for the Cloud Function.
1. Clone this repo and run the sample:
   ```
   python setup.py --webhook-url <CLOUD_FUNCTION_URL>
   ```
   where `<CLOUD_FUNCTION_URL>` is the URL of the Cloud Function you deployed
   in the previous step. The URL should take the following form:
   ```
   https://<REGION>-<PROJECT_ID>.cloudfunctions.net/dialogflow_webhook
   ```
   where `<REGION>` is the Google Cloud region of your function and
   `<PROJECT_ID>` is the Google Cloud project ID that contains your Cloud
   Function. For example:
   ```
   https://us-central1-my-project-id.cloudfunctions.net/dialogflow_webhook
   ```

## Running the sample

1. Go to the Dialogflow agent created by `setup.py` and query the agent:
