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

"""main.py creates a sample webhook handler for Dialogflow CX"""

import json

import google.cloud.dialogflowcx as cx


def basic_webhook(request):
    """Handles a Dialogflow CX webhook request."""
    request_dict = request.get_json()
    tag = request_dict["fulfillmentInfo"]["tag"]
    user_query = request_dict["text"]
    return json.dumps(
        {
            "fulfillment_response": {
                "messages": [
                    {
                        "text": {
                            "text": [f"Webhook received: {user_query} (Tag: {tag})"],
                            "allow_playback_interruption": False,
                        }
                    }
                ]
            }
        }
    )


def echo_webhook(request):
    """Echos the request that was received."""
    request_dict = request.get_json()
    request_json = json.dumps(request_dict)
    return json.dumps(
        {
            "fulfillment_response": {
                "messages": [
                    {
                        "text": {
                            "text": [request_json],
                        }
                    }
                ]
            }
        }
    )


def validate_form(request):
    """Validates that an age parameter from a form is sensible."""
    request_dict = request.get_json()
    parameter_info_list = request_dict["pageInfo"]["formInfo"]["parameterInfo"]

    parameter_dict = {}
    for parameter_info in parameter_info_list:
        key = parameter_info["displayName"]
        parameter_dict[key] = parameter_info["value"]

    if parameter_dict["age"] < 0:
        return json.dumps(
            {
                "fulfillment_response": {
                    "messages": [
                        {
                            "text": {
                                "text": [
                                    (
                                        f'Age {parameter_dict["age"]} not valid '
                                        "(must be positive)"
                                    )
                                ],
                            }
                        }
                    ]
                }
            }
        )
    return json.dumps(
        {
            "fulfillment_response": {
                "messages": [
                    {
                        "text": {
                            "text": ["Valid age"],
                        }
                    }
                ]
            }
        }
    )


def set_session_param(request):
    """Sets a session param detected in the intent."""
    request_dict = request.get_json()
    parameters = request_dict["sessionInfo"]["parameters"]
    key = parameters["key"]
    val = parameters["val"]
    return json.dumps(
        {
            "fulfillment_response": {
                "messages": [
                    {
                        "text": {
                            "text": ["Session parameter set"],
                        }
                    }
                ]
            },
            "session_info": {
                "parameters": {
                    key: val,
                    "key": None,
                    "val": None,
                }
            },
        }
    )


# [START TODO TAG]
def set_form_param_required(request):
    """Sets a form param (detected in the intent) as required."""
    request_dict = request.get_json()
    parameters = request_dict["sessionInfo"]["parameters"]
    last_matched_intent = request_dict["intentInfo"]["lastMatchedIntent"]
    param_to_set_as_required = parameters["parameter_name"]
    intent_components = cx.IntentsClient.parse_intent_path(last_matched_intent)
    project = intent_components["project"]
    location = intent_components["location"]
    agent = intent_components["agent"]
    parent = (
        f"projects/{project}/locations/{location}/agents/{agent}"
        "/flows/00000000-0000-0000-0000-000000000000"
    )
    request = cx.ListPagesRequest(parent=parent)
    client_options = {"api_endpoint": f"{location}-dialogflow.googleapis.com"}
    client = cx.PagesClient(
        client_options=client_options,
    )
    pages_dict = {p.display_name: p for p in client.list_pages(request=request)}
    page = pages_dict["Main Page"]

    for parameter in page.form.parameters:
        if parameter.display_name == param_to_set_as_required:
            parameter.required = True
            break

    request = cx.UpdatePageRequest(page=page)
    client.update_page(request)
    return json.dumps(
        {
            "fulfillment_response": {
                "messages": [
                    {
                        "text": {
                            "text": [
                                f"Form parameter {param_to_set_as_required} set as required"
                            ],
                        }
                    }
                ]
            },
            "session_info": {
                "parameters": {
                    "parameter_name": None,
                }
            },
        }
    )


# [END TODO TAG]


def webhook_fcn(request):
    """Delegates a request to an appropriate function, based on tag."""
    request_dict = request.get_json()
    tag = request_dict["fulfillmentInfo"]["tag"]
    if tag == "echo_webhook":
        return echo_webhook(request)
    if tag == "basic_webhook":
        return basic_webhook(request)
    if tag == "validate_form":
        return validate_form(request)
    if tag == "set_session_param":
        return set_session_param(request)
    if tag == "set_form_param_required":
        return set_form_param_required(request)
    raise RuntimeError(f"Unrecognized tag: {tag}")


def get_webhook_entrypoint() -> str:
    """Retursn the entrypoint for the main webhook delegator function."""
    return webhook_fcn.__name__


def get_webhook_name(build_uuid):
    """Builds a standardized webhook name for interaction with Cloud Functions."""
    entry_point = get_webhook_entrypoint()
    return f"{entry_point}_{build_uuid}"


def get_webhook_uri(project_id, build_uuid, region="us-central1"):
    """Returns the URI of the webhook deployed to Cloud Functions."""
    webhook_name = get_webhook_name(build_uuid)
    return f"https://{region}-{project_id}.cloudfunctions.net/{webhook_name}"


def build_request_dict_basic(tag, text):
    """Builds a dictionary matches the json structure of a Dialogflow request."""
    request_mapping = {"fulfillmentInfo": {}}
    request_mapping["fulfillmentInfo"]["tag"] = tag
    request_mapping["text"] = text
    return request_mapping


def extract_text(response_json: str, message_index=0):
    """Extracts the text response from the json response of a Dialogflow webhook."""
    response = json.loads(response_json)
    messages = response["fulfillment_response"]["messages"]
    return messages[message_index]["text"]["text"][0]


def extract_session_parameters(response_json: str):
    """Extracts session parameters from the json response of a Dialogflow webhook."""
    response = json.loads(response_json)
    return response["session_info"]["parameters"]
