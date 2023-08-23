# Blood Donation

## Overview

“Blood Donation” is a demo built on Dialogflow CX inspired
by the Australian Red Cross Lifeblood eligibility quiz.

Donate is a helpful and polite chatbot at "Save a life". Its task is to
assist people who want to donate blood and ensure they meet the required
eligibility requirements.

## Steps to build and deploy the agent

The export of the agent as a JSON package is located in the app root.
The steps to build and deploy the agent are illustrated in this
[codelab](https://codelabs.developers.google.com/codelabs/dialogflow-generator)

## Twilio integrations

The agent is integrated with Twilio Voice. To setup the voice integration, see
the [documentation](https://cloud.google.com/dialogflow/cx/docs/concept/integration/twilio).
To setup Twilio (Text Messaging) integration refer to this
[repository](https://github.com/GoogleCloudPlatform/dialogflow-integrations/tree/master/cx/twilio).

## Steps to build the web app

1. Install [Node.js](https://nodejs.org/en) using your preferred method or
   package manager
1. From this directory, run `npm install`
1. Run `npm start` to test your app locally

## Steps to deploy the web app to Firebase

1. Navigate to the [Firebase console](https://console.firebase.google.com/)
1. Provision Firebase on a new or existing GCP project
1. In Firebase console, go to Hosting and add a new site (e.g.,
   `your-firebase-app-name`)
1. Install the [firebase CLI](https://firebase.google.com/docs/cli)
1. Run `firebase init` in the app root and follow the prompts to select
   `Hosting`, use the `public` directory, configure it as a single-page app
   and confirm `N` to the followup
   questions about automatic builds and deploys.
1. Run
   `firebase target:apply hosting your-firebase-app-name your-firebase-app-name`
   where `your-firebase-app-name` is the name of the Firebase Hosting site that
   you created in an earlier step
1. To configure the default deploy target, add a line to your `firebase.json`
   with the name of your Firebase Hosting site, such as:

   ```json
   {
     "hosting": {
       "target": "your-firebase-app-name",  # <--- Add this line
       "public": "views",
       "ignore": [
         "firebase.json",
         "**/.*",
         "**/node_modules/**"
       ]
     }
   }
   ```

1. Run `firebase deploy`

## Access the app

In your browser, navigate to your deployed app using a URL similar to:

[https://blood-donation-agent.web.app/](https://blood-donation-agent.web.app/)

Congratulations, you've successfully deployed the Gen App Builder - Chat App
Demo!
