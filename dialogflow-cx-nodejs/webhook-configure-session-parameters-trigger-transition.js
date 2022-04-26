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
 * Configures a webhook to enable an agent response.
 */

// [START dialogflow_v3beta1_webhook_configure_session_parameters_trigger_transition]

// TODO (developer): change entry point to triggerTransition in Cloud Function

exports.triggerTransition = (request, response) => {
  // The value of the parameter used to trigger transition
  const sessionParameter =
    typeof request !== 'undefined'
      ? request.body.sessionInfo.parameters.value
      : 25;
  let text = '';
  let targetPage; // Must be format projects/<Project ID>/locations/<Location ID>/agents/<Agent ID>/flows/<Flow ID>/pages/<Page ID>

  if (sessionParameter > 15) {
    text = `You said ${sessionParameter}. Let me redirect you to our higher number department`;
    targetPage =
      'projects/<Project ID>/locations/<Location ID>/agents/<Agent ID>/flows/<Flow ID>/pages/<Page ID>';
  } else {
    text = `${sessionParameter} is a number I can help you with!`;
    targetPage =
      'projects/<Project ID>/locations/<Location ID>/agents/<Agent ID>/flows/<Flow ID>/pages/<Page ID>';
  }

  const jsonResponse = {
    target_page: targetPage,
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
  };

  response.send(jsonResponse);
};
// [END dialogflow_v3beta1_webhook_configure_session_parameters_trigger_transition]
