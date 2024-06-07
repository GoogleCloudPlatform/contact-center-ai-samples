import argparse
import datetime
import json
import random

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    "num_call_logs",
    nargs="?",
    default=10000,
    type=int,
    help="Number of call log files to generate",
)
args = parser.parse_args()
config = vars(args)

NUM_CALL_LOG_FILES = config["num_call_logs"]

greetings = [
    "Hello, how can I assist you today?",
    "Hi there, what can I help you with today?",
    "Greetings, how can I help you?",
    "Hi, welcome to support, how can I help you today?",
    "Hello, what can I assist you with?",
]

devices = [
    "television",
    "laptop",
    "router",
    "mobile phone",
    "smart watch",
    "tablet",
    "streaming device",
]

problems = [
    "The {0} doesn't seem to turn on. The {0} does not respond to any buttons or commands. The power light on the {0} does not turn on.",
    "The {0} is not connecting to the internet. The {0} cannot connect to a Wi-Fi network. The {0} cannot connect to the internet when plugged into a wired network.",
    "I cannot download any apps on my {0}. I am only able to access the messaging app on my {0}. I am not able to access other apps.",
    "I have not been able to connect to my account from my {0}. I cannot log into my account on my {0}. I cannot access my account on the {0}. I do not know what to do to fix my account.",
    "The battery on my {0} only lasts 30 minutes. The battery drains quickly after being fully charged. The {0} battery does not last as long as it used to.",
]

problem_detail = [
    "The {0} says that there is an error with the latest update. The {0} is stuck on the previous update. The update is not working properly on the {0}.",
    "It's been happening for the last 4 days, when I dropped the {0}. It's possible that the fall caused some damage to the {0}.",
    "The {0} isn't responding when I try to factory reset it. I changed the power settings a few days ago, and the {0} hasn't been working correctly since then.",
    "I tried using the troubleshooting wizard on the {0}, but it didn't help. There was a warning to check that the {0} has enough storage space and if it's compatible with the software I'm trying to use.",
    "The problem with the {0} is still happening since I last called in. I tried restarting the {0} 3 times and the issue is still happening. It's reporting a memory error about once an hour.",
]

statuses = [
    "Error: Failed update. The update is not available for your current major version. Please check for updates again later.",
    "All systems normal. Your device is connected to the internet and functioning normally. There are no issues to report.",
    "Warning: No available storage. Your computer's hard drive is full. Please delete some files and try again. You can also try to free up some space by moving some files to an external storage device.",
    "Error: Your account is not authorized to access this resource. Please contact the administrator for assistance.",
    "Warning: No connection to the internet. Your internet connection is blocked by a firewall. Please contact the administrator to unblock it.",
]

solutions = [
    "Have you tried turning the {0} off and on again? The {0} should be connected to the internet in order to contact our servers. If it is not, check your internet connection and make sure that your {0} is connected.",
    "Can you update your {0} to the latest firmware version? You can check if your {0}'s firmware is up to date by going to the {0}'s settings and looking for a firmware update option. If there is an update available, install it.",
    "Check if your {0} is able to access streaming content. You can check if your {0} is able to access streaming content by trying to watch a show or movie on a streaming service. If you are unable to watch anything, check your internet connection and make sure that your {0} is connected to the correct network.",
    "Check if your {0} are receiving a signal? You can check if your {0} are receiving a signal by using a signal strength meter. If the signal strength is low, you may need to move your {0} closer to the router.",
    "Have you tried to factory reset the {0}? You can check if your {0}'s settings are correct by going to the {0}'s settings and looking for a default settings option. If there is a default settings option, reset your {0} to the default settings.",
]

check_solved = [
    "Sure, does that cover everything for today?",
    "No problem, is there anything else that I can help with?",
    "Sure thing, did that solve the issue for you?",
    "Sounds good, are there any other issues that I can help with?",
    "Great, did that fix the problem?",
]

problem_solved = [
    "Yes, my problem is solved now. I have checked the settings on my {0} and made sure that everything is set up correctly.",
    "No, I'm still having the same problem. I will try contacting the manufacturer of the {0} for help.",
    "Yes, everything is working fine now. I have tried using a different connection to see if the problem is with the {0} or with the internet service provider.",
    "Yes, the {0} seems to be working now. I have checked the connections and made sure that everything is plugged in properly.",
    "No, I'm having a different problem now with the {0}. I have tried using a different website or app to see if the problem is with the website or app itself.",
]


def generate_log():
    # Select a device that the user is having trouble with
    device = random.choice(devices)

    # Generate timestamps within the last 30 days in microseconds of epoch time
    dt = datetime.datetime.today() - random.random() * datetime.timedelta(days=30)
    timestamp = int(round(dt.timestamp()) * 1e6)
    response_delay = int(random.randint(10, 30) * 1e6)

    # Generate JSON object of conversation
    call_log = {
        "entries": [
            {
                "start_timestamp_usec": timestamp + response_delay * 0,
                "text": random.choice(greetings),
                "role": "AGENT",
                "user_id": 2,
            },
            {
                "start_timestamp_usec": timestamp + response_delay * 1,
                "text": "Hi, I'm having an issue with my " + device,
                "role": "CUSTOMER",
                "user_id": 1,
            },
            {
                "start_timestamp_usec": timestamp + response_delay * 2,
                "text": "Sorry to hear. Can you tell me what the problem is?",
                "role": "AGENT",
                "user_id": 2,
            },
            {
                "start_timestamp_usec": timestamp + response_delay * 3,
                "text": random.choice(problems).format(device),
                "role": "CUSTOMER",
                "user_id": 1,
            },
            {
                "start_timestamp_usec": timestamp + response_delay * 4,
                "text": "Can you give me more details about the problem with your {0}?".format(device),
                "role": "AGENT",
                "user_id": 2,
            },
            {
                "start_timestamp_usec": timestamp + response_delay * 5,
                "text": random.choice(problem_detail).format(device),
                "role": "CUSTOMER",
                "user_id": 1,
            },
            {
                "start_timestamp_usec": timestamp + response_delay * 6,
                "text": "And what is the status shown in the settings on the {0}?".format(device),
                "role": "AGENT",
                "user_id": 2,
            },
            {
                "start_timestamp_usec": timestamp + response_delay * 7,
                "text": random.choice(statuses),
                "role": "CUSTOMER",
                "user_id": 1,
            },
            {
                "start_timestamp_usec": timestamp + response_delay * 8,
                "text": "Can you tell me your account number?",
                "role": "AGENT",
                "user_id": 2,
            },
            {
                "start_timestamp_usec": timestamp + response_delay * 9,
                "text": "Sure, it's " + str(random.randint(100000000, 999999999)),
                "role": "CUSTOMER",
                "user_id": 1,
            },
            {
                "start_timestamp_usec": timestamp + response_delay * 10,
                "text": random.choice(solutions).format(device),
                "role": "AGENT",
                "user_id": 2,
            },
            {
                "start_timestamp_usec": timestamp + response_delay * 11,
                "text": "I see, thanks for the information, I will give that a try.",
                "role": "CUSTOMER",
                "user_id": 1,
            },
            {
                "start_timestamp_usec": timestamp + response_delay * 12,
                "text": random.choice(check_solved),
                "role": "AGENT",
                "user_id": 2,
            },
            {
                "start_timestamp_usec": timestamp + response_delay * 13,
                "text": random.choice(problem_solved).format(device),
                "role": "CUSTOMER",
                "user_id": 1,
            },
        ]
    }

    json_object = json.dumps(call_log, indent=4)
    return json_object


for i in range(NUM_CALL_LOG_FILES):
    filename = "output/chat_" + str(i) + ".json"
    with open(filename, "w") as outfile:
        output = generate_log()
        outfile.write(output)
