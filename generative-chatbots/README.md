# Generative Chatbots

## Overview

These chatbots demonstrate the behavior of different
[generative AI](https://cloud.google.com/ai/generative-ai) features in
[Dialogflow CX](https://cloud.google.com/dialogflow/cx/docs/basics) when
answering questions about products in the
[Google Store](https://store.google.com/).

You can view the deployed version of the demo app at
[generative-chatbots.web.app](https://generative-chatbots.web.app/).

These virtual agents were built with
[generative AI](https://cloud.google.com/ai/generative-ai) functionality in
[Dialogflow CX](https://cloud.google.com/dialogflow/cx/docs/basics). The
[Data Store Agent](https://cloud.google.com/dialogflow/cx/docs/concept/data-store-agent)
chatbot queries indexed documents and data using
[Vertex AI Search](https://cloud.google.com/generative-ai-app-builder), and
each chatbot calls large language models (LLMs) in
[Vertex AI](https://cloud.google.com/vertex-ai) to generate dynamic,
personalized responses to users based on your website content, structured data,
or unstructured data. The static website is hosted on
[Firebase](https://firebase.google.com/) and is using the [Dialogflow CX
Messenger
integration](https://cloud.google.com/dialogflow/cx/docs/concept/integration/dialogflow-messenger).

You can learn more about each generative AI feature in
[Dialogflow CX](https://cloud.google.com/dialogflow/cx/docs/basics) by viewing
the documentation for
[Data Store Agent](https://cloud.google.com/dialogflow/cx/docs/concept/data-store-agent),
[Generative Fallback](https://cloud.google.com/dialogflow/cx/docs/concept/generative-fallback),
and
[Generators](https://cloud.google.com/dialogflow/cx/docs/concept/generators).
You can build these chatbots yourself by following the codelabs for
[Data Store Agent](https://codelabs.developers.google.com/codelabs/vertex-ai-conversation),
[Generative Fallback](https://codelabs.developers.google.com/codelabs/dialogflow-generative-fallback),
and
[Generators](https://codelabs.developers.google.com/codelabs/dialogflow-generator).
You can also learn more about
[Generative AI](https://cloud.google.com/ai/generative-ai) and
[Generative AI Use Cases](https://cloud.google.com/use-cases/generative-ai) in
Google Cloud.

## Steps to build the web app

1. Install [Node.js](https://nodejs.org/en) using your preferred method or
   package manager
1. From this directory, run `npm install`
1. Run `npm run dev` to preview the site locally
1. Run `npm run build` to generate the static site in the `build` directory

## Steps to deploy the web app to Firebase

1. Navigate to the [Firebase console](https://console.firebase.google.com/)
1. Provision Firebase on a new or existing GCP project
1. In Firebase console, go to Hosting and add a new site (e.g.,
   `your-firebase-app-name`)
1. Install the [firebase CLI](https://firebase.google.com/docs/cli)
1. Run `firebase init` in the app root and follow the prompts to select
   `Hosting`, use the `build` directory, and confirm `N` to the followup
   questions about rewrites, deploys, and the 404 and index pages.
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
       "public": "build",
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

[https://generative-chatbots.web.app](https://generative-chatbots.web.app)

Congratulations, you've successfully deployed the Generative Chatbots demo app!

## Additional resources

You can continue learning about conversational AI and generative AI with
these guides and resources:

- [Documentation for Dialogflow CX](https://cloud.google.com/dialogflow/cx/docs)
- [Documentation for Data Store Agent](https://cloud.google.com/dialogflow/cx/docs/concept/data-store-agent)
- [Documentation for Generative Fallback](https://cloud.google.com/dialogflow/cx/docs/concept/generative-fallback)
- [Documentation for Generators](https://cloud.google.com/dialogflow/cx/docs/concept/generators)
- [Generative AI in Google Cloud](https://cloud.google.com/ai/generative-ai)
