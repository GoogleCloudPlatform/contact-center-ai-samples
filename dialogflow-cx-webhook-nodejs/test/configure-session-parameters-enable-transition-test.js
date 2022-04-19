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

const {assert} = require('chai');
const {describe, it} = require('mocha');
const execSync = require('child_process').execSync;
const exec = cmd => execSync(cmd, {encoding: 'utf8'});

// projects/python-docs-samples-tests/locations/us-central1/agents/5b7712f3-034b-4647-9af6-a1b936cd057b/flows/e56e4f6f-5164-42b8-849c-fbc8c29ec2f8/flow_creation?pageId=047e518f-64f6-45ae-a347-955f3cd65a84
describe('configure session parameters to trigger transition', async () => {
  const cmd = 'node configure-session-parameters-enable-transition.js';
  const webhookUrl = process.env.WEBHOOK_URL;
  const agentId = process.env.AGENT;
  const flowId = process.env.FLOW_ID;
  const showBillDetailsPageId = '94f9e920-81c1-48b1-a06c-624d829a83c6';
  const suggestServiceCancellationPageId =
    '047e518f-64f6-45ae-a347-955f3cd65a84';

  it('should set target page based on `anomaly_detect == false` parameter value', async () => {
    const phoneNumber = '5105105100';
    const billMonth = 'current';

    const outputResponse = exec(
      `${cmd} ${phoneNumber} ${billMonth} ${webhookUrl} ${showBillDetailsPageId} ${suggestServiceCancellationPageId} ${agentId} ${flowId}`
    );
    console.log('webhook-response', outputResponse);
    assert.include(outputResponse, 'Target Page');
  });

  it('should set target page based on `anomaly_detect == true` parameter value', async () => {
    const phoneNumber = '9999999999';
    const billMonth = 'previous';

    const output = exec(
      `${cmd} ${phoneNumber} ${billMonth} ${webhookUrl} ${showBillDetailsPageId} ${suggestServiceCancellationPageId} ${agentId} ${flowId}`
    );
    console.log('webhook-response', output);
    assert.include(output, 'Target Page');
  });
});
