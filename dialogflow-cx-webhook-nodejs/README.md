# Dialogflow CX Webhooks Samples - Node.js

These webhooks samples use a **[prebuilt agent](https://cloud.google.com/dialogflow/cx/docs/concept/agents-prebuilt)**. Prebuilt agents are a collection of agents provided by Dialogflow for common use cases.

## Limitations

Prebuilt agents currently only support English (en).

## Import a prebuilt agent

These samples use the [Telecommunications Agent](https://cloud.google.com/dialogflow/cx/docs/concept/agents-prebuilt#telecommunications). To import the prebuilt agent to your project:

1. Go to the [Dialogflow CX Console](https://dialogflow.cloud.google.com/cx/projects).
2. Click the project where you would like to import the prebuilt agent.
3. Click **Use pre-built agents**.
4. Click the Telecommunications Agent, then click **Import**.
5. Choose your desired [location](/dialogflow/cx/docs/concept/region#avail) and click **Create**.
6. Some samples require the path to your agent. You can get the path by going to the list of agents in your project, clicking the 3-dot menu next to your selected agent, and clicking "Copy Name".

![image](https://user-images.githubusercontent.com/45905583/162499297-6e14e785-3ac6-41b3-9870-4b732b94151f.png)

8. Start testing and customizing.

## Modifying webhook code

The original webhook source
code uses Node.js and is hosted in Google's internal Cloud Functions project.

To use and modify this code in your own Cloud Functions project, please follow
the subsequent directions:

1. Go to the [`telecommunications-agent-webhook`](telecommunications-agent-webhook) directory in this repository.
2. Copy the source code.
3. Go to the Google Cloud Console and select **Cloud Functions** on the left panel.

![prebuilt-agents-cloud-functions](https://user-images.githubusercontent.com/45905583/162498119-2192e18f-562a-47bf-97b8-5b813180f380.png)

5. Click the project where you would like to import the source code.
6. Click **Create Function**.
   For further instructions, take a look at
   the [Create a Cloud Function](/functions/docs/create-deploy-nodejs#create_a_function)
   documentation.
6. Under the **Source code** section, select **Inline Editor** and paste the
   copied source code.
7. Click **Source** and then **Edit** to change the logic based on your
   business rules. Once finished, click **Deploy**.
8. Click **Trigger** and copy the **Trigger URL**.
9. Replace that Trigger URL in your agent by going to **Manage > Webhooks**
   and selecting the webhook to paste the new URL into. Paste the Trigger URL
   into the field labeled Webhook URL. Click **Save**.
