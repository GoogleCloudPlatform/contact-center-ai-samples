How To Export Voice Recording from a Genesys System for CCAI Insights

Purpose of this document

From time to time we run into customers that would like to use CCAI Insights to analyze call recordings but aren’t using CCAI or Dialogflow today.  Most regulated industries and most contact center platforms typically have a call recording capability.  Vendors in this space usually are numerous including Contact Center as a Platform (CCaas) like Genesys.  This document is intended to summarize for a customer and technical Googlers how to export call recordings from the Genesys Cloud Platform and import them successfully into CCAI Insights.

Pre-requisites:

Have admin access to a Genesys Instance
Have access to the AWS account where the exported data will be stored
Have the right permissions in AWS to create an S3 bucket, set permissions on the bucket, and create a KMS Key

Create IAM resources for AWS S3 bucket
Note: This article applies to the AWS S3 recording bulk actions integration.
To access AWS S3 functions, Genesys Cloud must have permission to use resources in your Amazon Web Services (AWS) account. This procedure explains how to create a policy, create an IAM role in AWS, and attach this role to the policy. Later you assign this role to the AWS S3 integration in Genesys Cloud.
Note: AWS Identity and Access Management (IAM) is a web service that controls access to AWS resources. An IAM role is similar to a user, because it defines an AWS identity with permission policies that determine what the identity can and cannot do in AWS. Trusted identities, including applications such as Genesys Cloud, AWS services such as EC2, or a user, assume the IAM role. Each IAM role defines necessary permissions to make AWS service requests. For more information, see IAM Roles in Amazon’s AWS Identity and Access Management User Guide.
To create a policy, create an IAM role, and attach this role to the policy, follow these steps:
Log in to AWS.
Navigate to the AWS Services page.
To create an S3 bucket, click S3. (Example below)



After you create an S3 bucket, go to the AWS Services page and click IAM.
Create a policy. Policies specify what resources roles can act on and how roles can act on the resources.
Under Dashboard, select Policies.
Click Create policy. 
On the Visual editor tab, configure the following items:
Under Service, click Select a service and click S3. This setting specifies what service the policy calls.
Under Actions and Access level, click the arrow next to Write and select the PutObject check box. This setting specifies what actions the policy grants to the AWS S3 bucket.
Under Read, select GetBucketLocation and GetEncryptionConfiguration.
Under Permission Management, select PutObjectAcl.
Under Resources, select Specific and click Add ARN. For Bucket Name, enter the name of the S3 bucket you created. For Object Name, check the box next to Any. Click Add.
Click Review policy.
In the Name box, type a name for the policy. 
Click Create policy.


Create a role that uses this policy.
Under Dashboard, click Roles.
On the Roles page, click Create role.
Select Another AWS Account as the type of trusted entity.
In the Account ID box, enter 765628985471 (Core/Satellite regions). This number is Genesys Cloud’s production account ID. If needed, please contact your Genesys representative for the FedRAMP region [US-East-2] account ID.
Select the Require external ID check box and enter your Genesys Cloud organization ID.
Click Next: Permissions.
Attach permission policies to this role.
Select the policy that you created.
Click Next: Tags
Click Next: Review.
In the Role name box, type a name for the role.
In the Role description box, enter descriptive text about the role.
Verify that the account number for Trusted entities matches the Genesys Cloud production AWS account ID that you entered earlier.
Click Create role.

Steps to create an Integration ID in Genesys for Bulk Export to AWS S3

You can export recordings, screen recordings, attachments and metadata, in bulk and store them in a configured S3 bucket. For more information, see Working with exported recordings in AWS S3 bucket.
To add the integration:
Click Admin.
Under Integrations, click Integrations.
Click the  Integration button.
Select AWS S3 Recording Bulk Actions Integration and click Install.
Click the Configuration tab.
Enter the name of the S3 bucket you created.
Optional: Enter a public key.
Click the Credentials tab.
Click Configure.
The Configure Credentials dialog box appears.
Enter the following information:
Role ARN: The role in your AWS account that has access to your AWS S3 bucket. This credential allows Genesys Cloud to access the AWS S3 bucket associated with this role.
Click OK.
Click Save. A list of all integrations that you have installed appears.
Activate the integration.

Note: If you do not activate the integration, then any recording bulk actions associated with the integration will not appear in Genesys Cloud applications.

The integration is now active. You can edit, deactivate, or delete an installed integration. For more information, see Edit, deactivate, or delete an integration. 
Create or edit a policy and enable Export Recording with Integration.
Note:
Exported recordings are exported using standard storage class. 
You can export archived recordings, but the process will take many hours to complete.
Orphan recordings are not exported unless the recording is recovered later.
Genesys Cloud exports recordings one time. If you create an export that matches a recording that has already been exported, that recording will be skipped.
A Genesys Cloud organization can only have a single instance of this integration active at a time.
If you configure a recording to be exported and deleted at the same time, the recording will first be exported and then deleted.
For the query parameters pageNumber and pageSize, values that are not valid are changed to the default values.



If set up is done properly and code executed successfully, you should see a response similar to the below depending on the action date and export window set:

Successfully execute recording bulk job {'date_created': datetime.datetime(2024, 1, 25, 21, 32, 43, 951000, tzinfo=tzutc()),
 'error_message': None,
 'failed_recordings': None,
 'id': '',
 'percent_progress': 0,
 'recording_jobs_query': {'action': 'EXPORT',
                          'action_age': None,
                          'action_date': datetime.datetime(2024, 1, 1, 0, 0, tzinfo=tzutc()),
                          'clear_export': None,
                          'conversation_query': {'conversation_filters': None,
                                                 'evaluation_filters': None,
                                                 'interval': '2023-12-01T00:00:00.000Z/2024-01-07T00:00:00.000Z',
                                                 'limit': None,
                                                 'order': 'asc',
                                                 'order_by': 'conversationStart',
                                                 'resolution_filters': None,
                                                 'segment_filters': None,
                                                 'start_of_day_interval_matching': False,
                                                 'survey_filters': None},
                          'include_recordings_with_sensitive_data': False,
                          'include_screen_recordings': True,
                          'integration_id': '##########',
                          'screen_recording_action_age': None,
                          'screen_recording_action_date': None},
 'self_uri': '/api/v2/recording/jobs/*****',
 'state': 'PROCESSING',
 'total_conversations': 337,
 'total_failed_recordings': 0,
 'total_processed_recordings': 0,
 'total_recordings': 303,
 'total_skipped_recordings': 0,
 'user': {'id': '******',
          'self_uri': '/api/v2/users/*****'}}
Successfully cancelled recording bulk job None
Successfully get recording bulk jobs {'entities': [],
 'first_uri': '/api/v2/recording/jobs?pageSize=25&pageNumber=1&sortBy=userId&state=READY&jobType=EXPORT&showOnlyMyJobs=true',
 'last_uri': '/api/v2/recording/jobs?pageSize=25&pageNumber=1&sortBy=userId&state=READY&jobType=EXPORT&showOnlyMyJobs=true',
 'next_uri': None,
 'page_count': 0,
 'page_number': 1,
 'page_size': 25,
 'previous_uri': None,
 'self_uri': '/api/v2/recording/jobs?pageSize=25&pageNumber=1&sortBy=userId&state=READY&jobType=EXPORT&showOnlyMyJobs=true',
 'total': 0}
