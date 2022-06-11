# Lambda EC2 Manager
Python serverless lambda function which would terminate all EC2 instances which don’t follow a tagging criteria.

AWS Lambda function runs every hour and checks EC2 instances which don’t have ‘Environment’ and ‘Name’ tags attached. If it finds an instance which doesn't have the aforementioned tags, it will send them an email to remind the user to tag the instance by using the ‘created by’ tag whose value would be an email id. Once 6 hours have passed after sending the email, it will terminate the instance with an email notifying the user of the same.


## Deployment Steps
1. Create **EC2 instances**
2. Create a **database** to store instances for which email was already sent. (Used jsonbin for fast but unsecured storage in this code).
3. Create **AWS SES**/SMTP (used SES here) to send emails. Create a new identity/existing and verify the same. 
4. Create an **AWS lambda function**. Write code in a virtual environnment and install required modules. Name the code file as 'lambda_function.py' and move it inside virtual env where the imported modules are present.
5. Zip all the files and upload to lambda.
6. Add environment variables under configuation as key value pairs.
7. Create an **IAM** with policies that allow lambda to use SES and other permissions required.
8. Create an empty test event.
9. Add a trigger - **EventBridge**. Create a new rule -> schedule expression with 1 hour cron/rate.
