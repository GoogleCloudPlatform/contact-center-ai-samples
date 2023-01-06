# Shirt Ordering Agent - Using Terraform with Dialogflow CX

Use Terraform to provision a Dialogflow CX agent in Google Cloud based on
[Create a Dialogflow CX
agent](https://cloud.google.com/dialogflow/cx/docs/quick/build-agent)
quickstart.

![Dialogflow CX Shirt Ordering Agent](images/store-order-agent.png)

# Prerequisites

* Register for a Google Cloud account (https://cloud.google.com/docs/get-started)
* Enable the Dialogflow API (https://cloud.google.com/dialogflow/cx/docs/quick/setup)
* Install and initialize the Google Cloud `gcloud` CLI tool (https://cloud.google.com/sdk/docs/install)
* Install Terraform (https://developer.hashicorp.com/terraform/downloads)

# Usage

1. Clone this repository and `cd` into this directory at `dialogflow-cx/shirt-ordering-agent`
1. Edit the values in `variables.tf`
1. Run `terraform init`
1. Run `terraform apply`

![Terraform Graph of Dialogflow CX Agent](images/order-agent-graph.png)
