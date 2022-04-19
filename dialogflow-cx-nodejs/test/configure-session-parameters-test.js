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

describe('validate parameter', async () => {
  const cmd = 'node configure-session-parameters.js';
  const webhookUrl = process.env.WEBHOOK_URL;

  it('should return newly created parameters', async () => {
    const phoneNumber = '5105105100';
    const billMonth = 'current';

    const output = exec(`${cmd} ${phoneNumber} ${billMonth} ${webhookUrl}`);
    console.log('updated-parameters', output);
    assert.include(output, 'purchase_amount');
    assert.include(output, 'first_month');
  });
});
