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

'use strict';

const axios = require('axios');

function main(phoneNumber, billMonth, webhookUrl) {
  // [START dialogflow_v3beta1_webhook_configure_session_parameters_enable_agent_response_async]
  /*
    TODO(developer): Uncomment these variables before running the sample.
    const phoneNumber = 'your-phone-line';
    const billMonth = 'your-bill-month';
    const webhookUrl = 'your-webhook-trigger-url';
  */

  // You can find the webhook logic for this sample on lines 15-78 in the Prebuilt Telecommunications Agent webhook (`telecommunications-agent-webhook/index.js`).
  // List of covered phone lines.
  // ['5555555555','5105105100','1231231234','9999999999]

  const webhookRequest = {
    fulfillmentInfo: {
      tag: 'detectCustomerAnomaly',
    },
    sessionInfo: {
      parameters: {
        phone_number: phoneNumber,
        bill_state: billMonth,
      },
    },
  };

  console.log('Webhook request', webhookRequest);

  async function configureSessionParametersEnableAgentResponse() {
    await axios({
      method: 'POST',
      url: webhookUrl,
      data: webhookRequest,
    })
      .then(res => {
        console.log('response body', res.data);
        // The WebhookResponse will return new parameters populated by the webhook logic.
        const updatedParameters = res.data.sessionInfo.parameters;

        // The webhook updates the `first_month` session parameter.
        console.log('First Month Session Parameter:');
        console.log(updatedParameters.first_month, '\n');

        // The configured parameter can be used in the fulfillment message returned by the webhook.
        console.log('Agent Response:');
        console.log(res.data.fulfillmentResponse.messages[0].text.text, '\n');
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
  // [END dialogflow_v3beta1_webhook_configure_session_parameters_enable_agent_response_async]

  configureSessionParametersEnableAgentResponse();
}

process.on('unhandledRejection', err => {
  console.error(err.message);
  process.exitCode = 1;
});

main(...process.argv.slice(2));
