// Copyright 2022 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * Configures a webhook to configure new session parameters
 */

// [START dialogflow_v3beta1_webhook_configure_optional_or_required_form_params]

// TODO (developer): change entry point to configureOptionalFormParam in Cloud Function

exports.configureOptionalFormParam = (request, response) => {
  let formParameter =
    typeof request !== 'undefined'
      ? request.body.pageInfo.formInfo.parameterInfo[0].value
      : 25;

  let isParamRequired = true;
  let paramState = 'VALID';
  let text = '';

  if (formParameter <= 15) {
    text = `${formParameter} is a number I can work with!`;
  }
  if (formParameter > 15 && formParameter < 20) {
    text = `${formParameter} is too many, but it's okay. Let's move on.`;
    isParamRequired = false;
  } else {
    text = `${formParameter} isn't going to work for me. Please try again!`;
    paramState = 'INVALID';
    formParameter = null;
  }

  const jsonResponse = {
    fulfillment_response: {
      messages: [
        {
          text: {
            //fulfillment text response to be sent to the agent
            text: [text],
          },
        },
      ],
    },
    pageInfo: {
      formInfo: {
        parameterInfo: [
          {
            displayName: formParameter,
            // if required: false, the agent will not reprompt for this parameter, even if the state is 'INVALID'
            required: isParamRequired,
            state: paramState,
          },
        ],
      },
    },
    // Set session parameter to null if you want to reprompt the user to enter a required parameter
    sessionInfo: {
      parameterInfo: {
        formParameter: formParameter,
      },
    },
  };

  response.send(jsonResponse);
};
// [END dialogflow_v3beta1_webhook_configure_optional_or_required_form_params]
