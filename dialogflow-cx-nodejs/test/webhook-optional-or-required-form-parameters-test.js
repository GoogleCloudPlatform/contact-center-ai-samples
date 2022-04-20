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

describe('optional or required parameters', async () => {
  const cmd = 'node webhook-optional-or-required-form-parameters.js';
  const webhookUrl = process.env.WEBHOOK_URL;

  it('should reprompt for required parameter if parameter status is `INVALID` ', async () => {
    const phoneNumber = '1952919481';
    const billMonth = 'current';
    const paramRequired = true;

    const output = exec(
      `${cmd} ${phoneNumber} ${billMonth} ${webhookUrl} ${paramRequired}`
    );
    console.log('required-parameter', output);
    assert.include(output, 'Sorry');
    assert.include(output, 'INVALID');
  });

  it('should NOT reprompt for optional parameter even if parameter status is `INVALID` ', async () => {
    const phoneNumber = '1952919481';
    const billMonth = 'current';
    const paramRequired = false;

    const output = exec(
      `${cmd} ${phoneNumber} ${billMonth} ${webhookUrl} ${paramRequired}`
    );
    console.log('required-parameter', output);
    assert.include(output, 'Sorry');
    assert.include(output, 'INVALID');
  });
});
