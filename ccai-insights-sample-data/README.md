# CCAI Insights Sample Data Generator

Generate sample chat log data in
[CCAI conversation data format](https://cloud.google.com/contact-center/insights/docs/conversation-data-format)
to use in CCAI Insights on Google Cloud.

## Usage

To generate sample chat logs, using the default of 10,000:

```bash
python generate-call-logs.py
```

Generate a different number of chat logs, such as 100:

```bash
python generate-call-logs.py 100
```

The sample data will be written as JSON files to the `output/` directory.

## Uploading to GCS

You can then upload the sample chat log data to Google Cloud Storage (GCS)
using the [`gsutil` tool](https://cloud.google.com/storage/docs/gsutil):

```bash
gsutil -m cp "output/*.json" gs://your-sample-chat-log-bucket
```

## Using Insights

Once you've generated and uploaded the sample data, you can [import the
conversations into CCAI Insights and analyze
them](https://cloud.google.com/contact-center/insights/docs/create-analyze-conversation-ui).

## Cleanup

After you're done using the sample data with Insights, you can edit the values
in the following script then run it to delete ALL conversation data in Insights
for cleanup purposes:

```
bash remove-all-conversations.sh
```

## Sample data

The sample data includes timestamps, text, role, and user ID for a support
conversation. Each support conversation will be written to a JSON file in the
`output/` directory and will appear similar to:

```json
{
    "entries": [
        {
            "start_timestamp_usec": 1675230581000000,
            "text": "Hi there, what can I help you with today?",
            "role": "AGENT",
            "user_id": 2
        },
        {
            "start_timestamp_usec": 1675230596000000,
            "text": "Hi, I'm having an issue with my mobile phone",
            "role": "CUSTOMER",
            "user_id": 1
        },
        {
            "start_timestamp_usec": 1675230611000000,
            "text": "Sorry to hear. Can you tell me what the problem is?",
            "role": "AGENT",
            "user_id": 2
        },
        {
            "start_timestamp_usec": 1675230626000000,
            "text": "I cannot download any apps. I am only able to access the messaging app. I am not able to access other apps.",
            "role": "CUSTOMER",
            "user_id": 1
        },
        {
            "start_timestamp_usec": 1675230641000000,
            "text": "Can you give me more details about the problem?",
            "role": "AGENT",
            "user_id": 2
        },
        {
            "start_timestamp_usec": 1675230656000000,
            "text": "It's been happening for the last 4 days, when I dropped the device. It's possible that the fall caused some damage to the device.",
            "role": "CUSTOMER",
            "user_id": 1
        },
        {
            "start_timestamp_usec": 1675230671000000,
            "text": "And what is the status shown in the application settings?",
            "role": "AGENT",
            "user_id": 2
        },
        {
            "start_timestamp_usec": 1675230686000000,
            "text": "All systems normal. Your device is connected to the internet and functioning normally. There are no issues to report.",
            "role": "CUSTOMER",
            "user_id": 1
        },
        {
            "start_timestamp_usec": 1675230701000000,
            "text": "Can you tell me your account number?",
            "role": "AGENT",
            "user_id": 2
        },
        {
            "start_timestamp_usec": 1675230716000000,
            "text": "Sure, it's 470908518",
            "role": "CUSTOMER",
            "user_id": 1
        },
        {
            "start_timestamp_usec": 1675230731000000,
            "text": "Check if your device is able to access streaming content. You can check if your device is able to access streaming content by trying to watch a show or movie on a streaming service. If you are unable to watch anything, check your internet connection and make sure that your device is connected to the correct network.",
            "role": "AGENT",
            "user_id": 2
        },
        {
            "start_timestamp_usec": 1675230746000000,
            "text": "I see, thanks for the information, I will give that a try.",
            "role": "CUSTOMER",
            "user_id": 1
        },
        {
            "start_timestamp_usec": 1675230761000000,
            "text": "Great, did that fix the problem?",
            "role": "AGENT",
            "user_id": 2
        },
        {
            "start_timestamp_usec": 1675230776000000,
            "text": "No, I'm having a different problem now. I have tried using a different website or app to see if the problem is with the website or app itself.",
            "role": "CUSTOMER",
            "user_id": 1
        }
    ]
}
```
