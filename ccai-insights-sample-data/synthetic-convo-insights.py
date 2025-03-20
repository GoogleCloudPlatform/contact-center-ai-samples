# generates synthetic conversation data utilizing Gemini 1.5 Flash
# includes fields for metadata
# formatted for successful import into CCAI Insights

import argparse
import datetime
import json
import random
import vertexai
import ast
import os
import time
import re
from google.oauth2 import service_account
from google.cloud import storage
from vertexai.preview.language_models import TextGenerationModel
from google.cloud import aiplatform
from google.api_core import retry
from google.api_core.exceptions import ServiceUnavailable
from vertexai.generative_models import GenerativeModel, GenerationConfig, Part, FinishReason
from collections import deque
from fuzzywuzzy import fuzz

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    "num_call_logs",
    nargs="?",
    default=10000, #UPDATE WITH NUMBER OF OUTPUT FILES YOU NEED
    type=int,
    help="Number of call log files to generate",
)
args = parser.parse_args()
config = vars(args)

NUM_CALL_LOG_FILES = config["num_call_logs"]

# Authentication
SERVICE_ACCOUNT_KEY_FILE = 'XXX.json'  # REPLACE WITH YOUR ACTUAL SERVICE ACCOUNT KEY FILE PATH
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_KEY_FILE)

# Project and Location Setup (Ensure they match your GCP project)
PROJECT_ID = '[Project ID]'  # REPLACE WITH YOUR PROJECT ID
LOCATION = 'us-central1'  # REPLACE AS NEEDED WITH YOUR CHOSEN REGION

# Vertex AI Initialization
vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=credentials)

# Create the Storage Client
storage_client = storage.Client(project=PROJECT_ID, credentials=credentials)

# Use Gemini 1.5 Flash model, change config variables as needed
model = GenerativeModel(model_name="gemini-1.5-flash-001")
generation_config = GenerationConfig(
    temperature=0.5,
    top_p=1.0,
    top_k=32,
    candidate_count=1,
    max_output_tokens=8192,
)

def generate_lists():
    # Prompts for Gemini to generate lists (CHANGE PROMPTS AS NEEDED BASED ON YOUR CUSTOMER)
    service_prompt = """I work for Ulta Beauty. Can you list out 5 common Ulta Beauty related issues customers may call customer support about? Feel free to use the https://www.ulta.com/ website for inspiration on common products or services or to learn more about the company. Make sure to be very specific about the exact product or service a customer is calling Ulta Beauty about. Your output should mirror this structure. 
    Example output: ["Service1","Service2","Service3","Service4","Service5"].Do not generate anything else other than the list"""
    problem_prompt = """List 5 common problems Ulta Beauty customers might have with their experience at Ulta Beauty. Be as specific and detailed as possible with customer responses, product types, issues, etc. Make sure to be very specific about the exact product, service, or issue a customer is calling about. Here is a website that give examples on common complaints Ulta Beauty customers may have: https://www.reddit.com/r/Ulta/. Here is another website that give examples on common complaints Ulta Beauty customers may have: https://www.bbb.org/us/il/bolingbrook/profile/retail-stores/ulta-beauty-0654-27005363/customer-reviews.  Your output should mirror this structure. 
    Example output: ["Problem1","Problem2","Problem3","Problem4","Problem5"].Do not generate anything else other than the list"""
    greeting_prompt = """List 5 different realistic ways an Ulta Beauty customer service representative might greet a customer on the phone, ensuring each greeting uses a UNIQUE and DISTINCT agent name. Include both a greeting and an offer to assist, mirroring Ulta Beauty's professional style. Replace '[Agent Name]' with a diverse range of realistic first names (both female and male). The agent names should be diverse, representing various genders and cultural backgrounds.
    Example output: ["Hello, thank you for calling Ulta Beauty. My name is Jose. How may I help you today?", "Welcome to Ulta Beauty! This is Ahmad. How can I assist you?", "Good morning/afternoon/evening! Thank you for contacting Ulta Beauty. This is David. What can I do for you today?","Hello, this is Ava with Ulta Beauty. How can I assist help you beautify your day?","It's a pleasure to assist you at Ulta Beauty. My name is Priya. How may I help you today?"]
    Do not generate anything else other than the list."""
    agent_name_prompt = """Generate a list of 50 DISTINCT and culturally diverse names that could be used for Ulta Beauty customer service representatives. Include names that are uncommon or less frequent, representing a wide range of ethnicities and genders. Ensure no repetition or similarity. 
    Example output: ["Jessica", "Priya", "Zaid", "Diego", "Luis"]."""
    closing_prompt = """List 5 different ways an Ulta Beauty customer service representative might end a call with a customer.Your output should mirror this structure. 
    Example output: ["Closing greeting1","Closing greeting2","Closing greeting3","Closing greeting4","Closing greeting5"].Do not generate anything else other than the list"""
    closing_response_prompt = """List 5 different ways a customer might respond to an Ulta Beauty customer service representative ending a call based off the last closing prompt message from the agent.
    Example output: ["Thank you for your help. Have a great day!", "You're welcome. Goodbye.", "No problem. Thanks for your time."]
    Do not generate anything else other than the list."""
    
    # Get responses from Gemini and clean up the output for CCAI Insights formatting
    services = model.generate_content(service_prompt)
    services_text = services.text.strip()[1:-1].replace('"', '').split(",")

    problems = model.generate_content(problem_prompt)
    problems_text = problems.text.strip()[1:-1].replace('"', '').replace("\n", "").split(",")

    greetings = model.generate_content(greeting_prompt)
    greetings_text = greetings.text.strip()[1:-1].replace('"', '').split(",")

    # Filter out unprofessional greetings and ensure Ulta Beauty is mentioned in the initial agent greeting
    greetings_text = list(
        filter(
            lambda g: "ulta beauty" in g.lower() and any(keyword in g.lower() for keyword in ["help", "assist", "welcome"]),
            greetings_text
        )
    )

    agent_names = model.generate_content(agent_name_prompt)
    agent_names_text = agent_names.text.strip()[1:-1].replace('"', '').split(",")

    closing_remarks = model.generate_content(closing_prompt)
    closing_remarks_text = closing_remarks.text.strip()[1:-1].replace('"', '').split(",")
    
    closing_responses = model.generate_content(closing_response_prompt)
    closing_responses_text = closing_responses.text.strip()[1:-1].replace('"', '').replace('-', '').split(",")

    #Parse with ast.literal_eval
    return services_text, problems_text, greetings_text, closing_remarks_text, closing_responses_text, agent_names_text

def generate_log(services, problems, greetings, closing_remarks, closing_responses, agent_names_buffer, max_retries=3, max_regeneration_retries=3):
    global shuffled_agent_names
    service = random.choice(services)
    problem_description = random.choice(problems)

    # Generate timestamps
     # Specify the desired start and end years, along with month/day ranges
    start_year = 2024    # Change to desired start year
    start_month = 1      # Change to desired start month
    start_day = 1       # Change to desired start day
    end_year = 2024      # Change to desired end year
    end_month = 9       # Change to desired end month
    end_day = 3         # Change to desired end day
    
    # Generate random timestamps within the specified range
    def generate_random_timestamp():
        start_date = datetime.datetime(year=start_year, month=start_month, day=start_day)
        end_date = datetime.datetime(year=end_year, month=end_month, day=end_day, hour=23, minute=59, second=59)
    
        random_datetime = start_date + random.random() * (end_date - start_date)
        return int(random_datetime.timestamp() * 1000000)
    
    # Generate timestamp and response delay
    timestamp = generate_random_timestamp()
    response_delay = random.randint(5000000, 10000000)  # 5 to 10 seconds for all roles

    # Increased regeneration threshold (adjust as needed)
    regeneration_threshold = 3  # Lowered threshold for more frequent regeneration

    if len(agent_names_buffer) < 2:
        for _ in range(max_regeneration_retries):
            print("Regenerating agent names and greetings for more variety...")
            services, problems, greetings, closing_remarks, closing, new_agent_names = generate_lists()  # Regenerate greetings as well
            agent_names_buffer.extend(new_agent_names)
            if len(agent_names_buffer) >= 2:
                break
        else:
            print("Max regeneration retries reached. Skipping this call log.")
            return None

    customer_behavior = random.choice(["polite and patient", "frustrated and impatient", "angry and demanding", "confused and unsure"])

    # Generate a natural problem statement
    problem_statement_prompt = f"""
    Rewrite this issue into a natural statement a customer would say to describe their problem with their {service}: "{problem_description}" at the BEGINNING of their call. Make sure the customer provides context to their issue.
    """

    for retry_count in range(max_retries):
        try:
            problem_statement_response = model.generate_content(problem_statement_prompt)

            # Check for safety filter blocks in any candidate
            for candidate in problem_statement_response.candidates:
                if candidate.finish_reason == "STOP_REASON_SAFETY":
                    raise Exception("Safety filter triggered. Retrying...")

            customer_statement = problem_statement_response.text.strip()

            # --- Generate Metadata (but don't extract agent name yet) ---
            call_id = random.randint(1000, 999999)
            #language_code = "en-US"
            #call_type = random.choice(["inbound", "outbound"])
            channel = random.choice(["phone", "chat"])  # Randomly chooses phone or chat
            #agent_group = random.choice(["Tier 1 Support", "Billing"])
            agent_experience = random.choice(["junior", "senior", "manager", "supervisor", "trainee"])
            agent_location = random.choice(["US", "India", "EMEA"])
            customer_id = random.randint(100, 9999)
            customer_sentiment = "positive" if customer_behavior == "polite and patient" else "negative"  # Example inference
            customer_region = random.choice(["East Coast", "West Coast", "Central"])



            prompt_template = f"""
            Create a customer support transcript where an Ulta Beauty agent helps a customer with their {service}.
            The conversation starts with the agent's greeting.
            Adhere strictly to this format:
            Agent: {random.choice(greetings)}
            Customer: {customer_statement}
            Agent: [Agent's response acknowledging the problem and starting troubleshooting]
            Customer: [Customer's response to the troubleshooting steps]
            Agent: [Further troubleshooting or resolution steps]
            ... (continue the back-and-forth as needed)
            Agent: [Resolution of the issue or escalation]
            Agent: {random.choice(closing_remarks)}
            Customer: [Customer's natural response acknowledging resolution and ending the call]

            Additional instructions:

            *   Use "{random.choice(greetings)}" for the agent's greeting.
            *   Use "{random.choice(closing_remarks)}" for the agent's closing remark.
            *   The conversation MUST include troubleshooting steps and a resolution.
            *   Focus on a single core issue the customer is experiencing
            *   The customer is "{customer_behavior}"
            """

            print(prompt_template)

            response = model.generate_content(prompt_template, generation_config=generation_config)

            transcript = response.text

            # Check for safety filter blocks in any candidate (not just the first one)
            for candidate in response.candidates:
                if candidate.finish_reason == "STOP_REASON_SAFETY":
                    raise Exception("Safety filter triggered. Retrying...")

            # Enhanced Transcript Parsing with Logic to Prevent Unnatural Endings
            entries = []
            current_speaker = None
            customer_said_no = False
            short_customer_response = False
            agent_asked_anything_else = False
            last_agent_line = ""

            for line in transcript.splitlines():
                line = line.strip()
                if line.lower().startswith("customer") or line.lower().startswith("agent"):
                    if line.lower().startswith("customer"):
                        entries.append({"role": "CUSTOMER", "text": line[8:].strip(), "user_id": 1})
                        if line.lower().strip() in ["no", "no thanks", "that's all", "that's it", "i'm good", "nothing else","okay"]:
                            customer_said_no = True
                        if len(line.lower().strip()) <= 3:
                            short_customer_response = True
                    elif line.lower().startswith("agent"):
                        last_agent_line = line[5:].strip()
                        if "anything else" in last_agent_line.lower():
                            agent_asked_anything_else = True
                        
                        # Condition to skip the "anything else" response after customer says no
                        if not (customer_said_no and "anything else" in last_agent_line.lower()):
                            entries.append({"role": "AGENT", "text": line[5:].strip(), "user_id": 2})

            # Check if the first agent entry has a proper greeting (with fuzzy matching)
            if entries and entries[0]["role"] == "AGENT":
                agent_greeting = entries[0]["text"].lower()
            
                # Define a list of acceptable greeting keywords/phrases
                greeting_keywords = ["help", "assist", "welcome", "hello", "hi", "good morning", "good afternoon", "good evening"]
            
                # Check if any of the greeting keywords/phrases have a high similarity score with the agent's greeting
                has_valid_greeting = any(
                    fuzz.partial_ratio(keyword, agent_greeting) > 80
                    for keyword in greeting_keywords
                )
            
                if not has_valid_greeting:
                    print("Agent's greeting is missing or incomplete (fuzzy matching). Retrying...")
                    return generate_log(services, problems, greetings, closing_remarks, closing_responses, agent_names)
            
            # Additional check for the first few agent turns
            for i, entry in enumerate(entries[:3]):  # Check the first 3 agent turns
                if entry["role"] == "AGENT":
                    if any(product.lower() in entry["text"].lower() for product in services):
                        print("Agent assumed the product too early. Retrying...")
                        return generate_log(services, problems, greetings, closing_remarks, closing_responses, agent_names)

            # Retry Conditions (consolidated for readability)
            if any((
                agent_asked_anything_else and last_agent_line == entries[-1]['text'],
                customer_said_no and "anything else" in last_agent_line.lower(),
                short_customer_response,
                not entries  # Check for blank output
            )):
                retry_reason = (
                    "Customer didn't answer 'anything else?'"
                    if agent_asked_anything_else
                    and last_agent_line == entries[-1]["text"]
                    else "Agent asked again after customer said no"
                    if customer_said_no and "anything else" in last_agent_line.lower()
                    else "Customer response too short"
                    if short_customer_response
                    else "Blank output"
                )
                print(f"{retry_reason}. Retrying...")
                return generate_log(
                    services,
                    problems,
                    greetings,
                    closing_remarks,
                    closing_responses,
                    agent_names,
                )

            # Add timestamps
            for i, entry in enumerate(entries):
                entry["start_timestamp_usec"] = timestamp + response_delay * i



            # *** Extract agent name AFTER populating entries ***
            agent_name_found = False
            for entry in entries:
                if entry["role"] == "AGENT":
                    # Try to find the agent name using the regular expression
                    match = re.search(
                        r"(?:my name is|this is|i'm)\s+([\w\s]+)",
                        entry["text"],
                        re.IGNORECASE,
                    )
                    if match:
                        agent_name = match.group(1).strip()
                        agent_name_found = True
                        break  # Stop after finding the agent name

            if not agent_name_found:
                # Handle the case where no agent name is found in the transcript
                print("No agent greeting found in the transcript. Retrying...")
                return generate_log(
                    services,
                    problems,
                    greetings,
                    closing_remarks,
                    closing_responses,
                    agent_names_buffer,
                )



            # Generate a unique Agent ID (you can customize this logic)
            agent_id = random.randint(1000, 9999)
            
            # Replace any remaining placeholders
            #for entry in entries:
             #   if "[agent name]" in entry["text"].lower():
              #      entry["text"] = entry["text"].replace("[agent name]", agent_name_for_transcript)

            
            # Add agent metadata to each agent entry
            for entry in entries:
                if entry["role"] == "AGENT":
                    entry["agent_name"] = agent_name  # Use the extracted agent_name
                    entry["agent_id"] = agent_id

            
            # --- Create metadata dictionary ---
            metadata = {
                "call_id": call_id,
                #"language_code": language_code,
                #"call_type": call_type,
                "channel": channel,
                #"agent_group": agent_group,
                "agent_experience": agent_experience,
                "agent_location": agent_location,
                "customer_id": customer_id,
                "customer_sentiment": customer_sentiment,
                "customer_region": customer_region,
                "agent_id": agent_id,
                # ... add more metadata as needed
            }


            call_log = {
                "entries": entries,
                "metadata": metadata,
            }  # Include metadata in the call_log
            json_object = json.dumps(call_log, indent=4)
            return json_object  # Return the generated JSON if successful

        except Exception as e:
            print(f"Error generating log (attempt {retry_count + 1}/{max_retries}): {e}")
            if retry_count < max_retries - 1:
                time.sleep(2 ** retry_count)
            else:
                print("Max retries reached. Skipping this call log.")
                return None


# Main execution loop

services, problems, greetings, closing_remarks, closing, agent_names = generate_lists()
random.shuffle(agent_names)  # Shuffle the entire list once at the beginning

# Create a circular buffer (deque) from the shuffled agent names
agent_names_buffer = deque(agent_names)

# Main execution loop
for i in range(NUM_CALL_LOG_FILES):
    json_object = generate_log(services, problems, greetings, closing_remarks, closing, agent_names_buffer)

    if json_object is not None:  # Only save if generation was successful
        # Upload to GCS with overwrite prevention
        bucket = storage_client.bucket("ulta-enriched4") #UPDATE WITH YOUR GCS BUCKET
        base_filename = f"gem_chat_{i}_np.json" #CHANGE FILE NAME AS NEEDED
        filename = base_filename
        counter = 1

        blob = bucket.blob(filename)
        while blob.exists():  # Check for existing blob
            filename = f"{os.path.splitext(base_filename)[0]}_{counter}.json"
            blob = bucket.blob(filename)  # Update the blob reference
            counter += 1

         # Retry mechanism for blob upload
        @retry.Retry(predicate=retry.if_exception_type(ServiceUnavailable), deadline=60)
        def upload_blob():
            blob.upload_from_string(json_object)

        try:
            upload_blob()
            print(f"Uploaded {filename} to GCS bucket ulta-enriched4") #UPDATE WITH YOUR GCS BUCKET
        except Exception as e:  # Catch any remaining errors
            print(f"Upload failed after retries: {e}")
    else:
        print(f"Skipping call log {i} due to an error.")
