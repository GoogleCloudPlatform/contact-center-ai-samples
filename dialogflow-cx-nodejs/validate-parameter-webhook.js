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
 * Uses a webhook to validate form parameters.
 *
 * See https://cloud.google.com/dialogflow/cx/docs/quick/api before running the code snippet.
 */

'use strict';

function main(phoneNumber, webhookUrl) {
  // [START dialogflow_v3beta1_webhook_validate_form_parameters_async]

  // TODO(developer): Uncomment these variables before running the sample.
  // const phoneNumber = 'your-phone-line';
  // const webhookUrl = 'your-webhook-trigger-url';

  // Webhook will verify if customer phone number is valid (included in the list of covered phone lines). You can find the webhook logic in lines 85-162 in the Prebuilt Telecommunications Agent `telecommunications-agent-webhook/index.js`.
  // List of covered phone lines.
  // ['5555555555','5105105100','1231231234','9999999999]

  // Imports axios
  const axios = require('axios');

  // Creates a JSON representation of a WebhookRequest object
  const webhookRequest = {
    fulfillmentInfo: {
      // Webhook uses tag to determine which function to execute
      tag: 'validatePhoneLine',
    },
    sessionInfo: {
      parameters: {
        phone_number: phoneNumber,
      },
    },
  };

  // Calls the webhook service. Validates/invalidates the parameter and handles the response
  async function validateParameter() {
    await axios({
      method: 'POST',
      url: webhookUrl,
      data: webhookRequest,
    })
      .then(res => {
        console.log('response body', res.data);
        const fulfillmentResponseMessage =
          res.data.fulfillmentResponse.messages[0].text.text[0];

        const parameterInfoState =
          res.data.pageInfo.formInfo.parameterInfo[0].state;

        console.log('Fulfillment Response:');
        console.log(fulfillmentResponseMessage, '\n');

        console.log('Parameter Status:');
        console.log(parameterInfoState, '\n'); // Parameter state: 'VALID' or 'INVALID'

        // If parameter status is 'INVALID', resets the session parameter state to `null` so that the user can enter a new input
        console.log('Phone Number parameter value:');
        console.log(res.data.sessionInfo.parameters.phone, '\n');
      })
      .catch(err => {
        if (err.response) {
          console.log(
            'Client was given an error response\n',
            err.response.data
          );
        } else if (err.request) {
          console.log(
            'Client never received an error response\n',
            err.request.data
          );
        } else {
          console.log(err.message);
        }
      });
  }
  // [END dialogflow_v3beta1_webhook_validate_form_parameters_async]

  validateParameter();
}

process.on('unhandledRejection', err => {
  console.error(err.message);
  process.exitCode = 1;
});

main(...process.argv.slice(2));
