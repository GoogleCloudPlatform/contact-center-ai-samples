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

function main(
  phoneNumber,
  billMonth,
  webhookUrl,
  showBillDetailsPageId,
  suggestServiceCancellationPageId,
  agentId,
  flowId
) {
  // [START dialogflow_v3beta1_webhook_configure_session_parameters_enable_transition_async]
  /*
    TODO(developer): Uncomment these variables before running the sample.
    const phoneNumber = 'your-phone-line';
    const billMonth = 'your-bill-month';
    const webhookUrl = 'your-webhook-trigger-url';
    const agentId = 'your-agent-id'; Format 'projects/<Project ID>/locations/<Location ID>/agents/<Agent ID>/flows/<Flow ID>/pages/<Page ID>'
    const flowId = 'your-flow-id';
    const showBillDetailsPageId = 'your-transition-page-id';
    const suggestServiceCancellationPageId = 'another-transition-page-id';
  */

  // You can find the webhook logic for this sample on lines 15-84 in the Prebuilt Telecommunications Agent webhook (`telecommunications-agent-webhook/index.js`).
  // List of covered phone lines.
  // ['5555555555','5105105100','1231231234','9999999999']

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
    payload: {
      fields: {
        show_bill_details_page_id: showBillDetailsPageId,
        suggest_service_cancellation_page_id: suggestServiceCancellationPageId,
        agentId: agentId,
        flowId: flowId,
      },
    },
  };

  console.log('Webhook request', webhookRequest);

  async function configureSessionParametersEnableTransition() {
    await axios({
      method: 'POST',
      url: webhookUrl,
      data: webhookRequest,
    })
      .then(res => {
        console.log('response body', res.data);
        // The WebhookResponse will return the target page based on the session parameter value.
        const targetPage = res.data.targetPage;
        const responseMessage =
          res.data.fulfillmentResponse.messages[0].text.text;

        console.log('Agent Response: ', responseMessage, '\n');
        console.log('Target Page: ', targetPage, '\n');
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
  // [END dialogflow_v3beta1_webhook_configure_session_parameters_enable_transition_async]

  configureSessionParametersEnableTransition();
}

process.on('unhandledRejection', err => {
  console.error(err.message);
  process.exitCode = 1;
});

main(...process.argv.slice(2));
