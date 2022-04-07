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

// BEGIN validatePhoneLine
// case 'validatePhoneLine':
// [START dialogflow_v3beta1_webhook_validate_form_parameters_async]

// {
//     "detectIntentResponseId": string,
//     "languageCode": string,
//     "fulfillmentInfo": {
//       object (FulfillmentInfo)
//     },
//     "intentInfo": {
//       object (IntentInfo)
//     },
//     "pageInfo": {
//       object (PageInfo)
//     },
//     "sessionInfo": {
//       object (SessionInfo)
//     },
//     "messages": [
//       {
//         object (ResponseMessage)
//       }
//     ],
//     "payload": {
//       object
//     },
//     "sentimentAnalysisResult": {
//       object (SentimentAnalysisResult)
//     },

//     // Union field query can be only one of the following:
//     "text": string,
//     "triggerIntent": string,
//     "transcript": string,
//     "triggerEvent": string
//     // End of list of possible types for union field query.
//   }

// TODO: change entry point to handleWebhook in cloud function

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
const helpers = require('./helpers.js')

function main(destination, webhookUrl) {
  // [START dialogflow_v3beta1_webhook_validate_form_parameters_async]
  /*
    TODO(developer): Uncomment these variables before running the sample.
    const destination = 'your-cruise-destination';
    const webhookUrl = 'your-webhook-trigger-url';
  */

    // Webhook will verify if cruise destination port is covered.
    // Sample list of covered cruise ports.
    // [ 'mexico', 'canada', 'anguilla']

  const webhookRequest = {
    fulfillmentInfo: {
      tag: 'cruisePlanCoverage',
    },
    sessionInfo: {
      parameters: {
        destination: destination,
      },
    },
  };

  async function validateParameter() {
    await axios({
      method: 'POST',
      url: webhookUrl,
      data: {
        webhookRequest,
      },
    }).then(res => {
      const fulfillmentResponseMessage =
        res.data.sessionInfo.parameters.port_is_covered;
      const parameterInfoState =
        res.data.pageInfo.formInfo.parameterInfo[0].state;

      console.log('Fulfillment Response:');
      console.log(fulfillmentResponseMessage, '\n'); // 'true' or 'false'

      console.log('Parameter Status:');
      console.log(parameterInfoState, '\n'); // Parameter state: 'VALID' or 'INVALID'
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