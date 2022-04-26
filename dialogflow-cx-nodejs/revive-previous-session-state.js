// Copyright 2021 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * Revives the state of a previous session
 *
 * See https://cloud.google.com/dialogflow/cx/docs/quick/api before running the code snippet.
 */

'use strict';

async function main(projectId, location, agentId, query, languageCode) {
  // [START dialogflow_v3beta1_revive_previous_session_state_async]

  // projectId = 'my-project';
  // location = 'global';
  // agentId = 'my-agent';
  // query = 'Hello!';
  // languageCode = 'en';

  // Imports the Google Cloud Dialogflow CX API library
  const {SessionsClient} = require('@google-cloud/dialogflow-cx');

  const uuid = require('uuid');

  // Example for regional endpoint:
  // const location = 'us-central1'
  // const client = new SessionsClient({apiEndpoint: 'us-central1-dialogflow.googleapis.com'})

  // Instantiates the Dialogflow CX Sessions Client
  const client = new SessionsClient();

  // Create a function that can marshal the current session state to JSON:
  function marshalSession(response) {
    const sessionRestartData = {
      currentPage: response.queryResult.currentPage.name,
      parameters: response.queryResult.parameters,
    };
    return sessionRestartData;
  }

  async function detectFirstSessionIntent() {
    // Marshalls the current state:
    const sessionId = uuid.v4();
    const sessionPath = client.projectLocationAgentSessionPath(
      projectId,
      location,
      agentId,
      sessionId
    );
    console.info(sessionPath);

    // Creates a JSON representation of a DetectIntentRequest object
    const request = {
      session: sessionPath,
      queryParams: {
        parameters: {
          fields: {
            firstName: {kind: 'stringValue', stringValue: 'John'},
            lastName: {kind: 'stringValue', stringValue: 'Doe'},
          },
        },
      },
      queryInput: {
        text: {
          text: query,
        },
        languageCode,
      },
    };
    console.log(`User Query: ${query}`);

    // Detects intent of the user query
    const [response] = await client.detectIntent(request);

    // Processes the DetectIntentResponse
    for (const message of response.queryResult.responseMessages) {
      if (message.text) {
        console.log(`Agent Response: ${message.text.text}`);
      }
    }
    if (response.queryResult.match.intent) {
      console.log(
        `Matched Intent: ${response.queryResult.match.intent.displayName}`
      );
    }
    return marshalSession(response);
  }

  // Revives the previous session state
  async function revivePreviousSessionState() {
    // Unmarshalls the saved state:
    const firstSessionDict = await detectFirstSessionIntent();

    // Assigns the values of the previous session to the current session
    const currentPage = firstSessionDict['currentPage'];
    const parameters = firstSessionDict['parameters'];

    // Creates a JSON representation of a QueryParameters object
    const queryParams = {
      currentPage: currentPage,
      parameters: parameters,
    };

    // Creates a unique session ID
    const sessionId = uuid.v4().toString;

    // Creates a JSON representation of a DetectIntentRequest object
    const secondRequest = {
      session: client.projectLocationAgentSessionPath(
        projectId,
        location,
        agentId,
        sessionId
      ),
      queryInput: {
        text: {
          text: 'Hello 60 minutes later!',
        },
        languageCode: 'en-US',
      },
      queryParams: queryParams,
    };

    // Detects intent of the user query
    const [secondResponse] = await client.detectIntent(secondRequest);

    // Previous session parameters are revived in the second session
    console.log(` Revived Session Parameters:
      ${JSON.stringify(secondResponse.queryResult.parameters)}`);
    console.log(` Revived Session Query Text:
      ${JSON.stringify(secondResponse.queryResult.text)}`);
  }

  revivePreviousSessionState();
  // [END dialogflow_v3beta1_revive_previous_session_state_async]
}

process.on('unhandledRejection', err => {
  console.error(err.message);
  process.exitCode = 1;
});
main(...process.argv.slice(2));
