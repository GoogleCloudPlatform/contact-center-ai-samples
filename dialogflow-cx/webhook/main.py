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
