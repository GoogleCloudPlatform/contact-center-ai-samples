import os
import sys
import time
import PureCloudPlatformClientV2
from PureCloudPlatformClientV2.rest import ApiException

print("-------------------------------------------------------------")
print("- Execute Bulk Action on recordings-")
print("-------------------------------------------------------------")

# Credentials for the aws bucket
CLIENT_ID = ""
CLIENT_SECRET = ""
ORG_REGION = ""

# Set environment
region = PureCloudPlatformClientV2.PureCloudRegionHosts[ORG_REGION]
PureCloudPlatformClientV2.configuration.host = region.get_api_host()

# OAuth when using Client Credentials
api_client = (
    PureCloudPlatformClientV2.api_client.ApiClient().get_client_credentials_token(
        CLIENT_ID, CLIENT_SECRET
    )
)


# Get the api
recording_api = PureCloudPlatformClientV2.RecordingApi(api_client)

# Build the create job query, for export action, set query.action = "EXPORT"
# For delete action, set query.action = "DELETE"
# For archive action, set query.action = "ARCHIVE"
query = PureCloudPlatformClientV2.RecordingJobsQuery()
query.action = "EXPORT"
query.action_date = "2024-01-25T00:00:00.000Z"
# Comment out integration id if using DELETE or ARCHIVE
query.integration_id = ""
query.conversation_query = {
    "interval": "2023-12-01T00:00:00.000Z/2024-01-07T00:00:00.000Z",
    "order": "asc",
    "orderBy": "conversationStart",
}
print(query)
try:
    # Call create_recording_job api
    create_job_response = recording_api.post_recording_jobs(query)
    job_id = create_job_response.id
    print(f"Successfully created recording bulk job { create_job_response}")
    print(job_id)
except ApiException as e:
    print(f"Exception when calling RecordingApi->post_recording_jobs: { e }")
    sys.exit()


# Call get_recording_job api
while True:
    try:
        get_recording_job_response = recording_api.get_recording_job(job_id)
        job_state = get_recording_job_response.state
        if job_state != "PENDING":
            break
        else:
            print("Job state PENDING...")
            time.sleep(2)
    except ApiException as e:
        print(f"Exception when calling RecordingApi->get_recording_job: { e }")
        sys.exit()


if job_state == "READY":
    try:
        execute_job_response = recording_api.put_recording_job(
            job_id, {"state": "PROCESSING"}
        )
        job_state = execute_job_response.state
        print(f"Successfully execute recording bulk job { execute_job_response}")
    except ApiException as e:
        print(f"Exception when calling RecordingApi->put_recording_job: { e }")
        sys.exit()
else:
    print(f"Expected Job State is: READY, however actual Job State is: { job_state }")


# Call delete_recording_job api
# Can be canceled also in READY and PENDING states
if job_state == "PROCESSING":
    try:
        cancel_job_response = recording_api.delete_recording_job(job_id)
        print(f"Successfully cancelled recording bulk job { cancel_job_response}")
    except ApiException as e:
        print(f"Exception when calling RecordingApi->delete_recording_job: { e }")
        sys.exit()


try:
    get_recording_jobs_response = recording_api.get_recording_jobs(
        page_size=25,
        page_number=1,
        sort_by="userId",  # or "dateCreated"
        state="READY",  # valid values FULFILLED, PENDING, READY, PROCESSING, CANCELLED, FAILED
        show_only_my_jobs=True,
        job_type="EXPORT",  # or "DELETE"
    )
    print(f"Successfully get recording bulk jobs { get_recording_jobs_response}")
except ApiException as e:
    print(f"Exception when calling RecordingApi->get_recording_jobs: { e }")
    sys.exit()
