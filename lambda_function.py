import boto3
import os
import requests
from datetime import datetime

AWS_ACCESS_KEY = os.environ['aws_access_key_id']
AWS_SECRET_KEY = os.environ['aws_secret_access_key']
AWS_REGION = os.environ['region']
SOURCE = os.environ['sender_email']

# Storing JSON in jsonbin
API_KEY = os.environ['bin_id']
BIN_ID = os.environ['api_key']

url = f'https://api.jsonbin.io/v3/b/{BIN_ID}'
headers = {
  'Content-Type': 'application/json',
  'X-Master-Key': API_KEY
}

ec2 = boto3.resource('ec2', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)

def terminate_instance(id):
    ec2.instances.filter(InstanceIds=id).terminate()

def send_email(receiver_email, tags, instance_id, instances_db):
    client = boto3.client('ses')
    receiver_name = receiver_email.split('@')[0]
    tags_parsed = '\n'.join(tags)
    email_body = f'Hi {receiver_name},\n\nYour EC2 instance({instance_id}) is missing the following tags:\n{tags_parsed}.\n\nPlease tag them to avoid termination in 6 hours.\n\nThanks.'

    try:
        receiver_email = 'tterter960@gmail.com'
        response = client.send_email(
            Source=SOURCE,
            Destination={
                'ToAddresses': [
                    receiver_email,
                ]
                },
            Message={
                'Subject': {
                    'Data': 'Subject'
                },
                'Body': {
                    'Text': {
                        'Data': email_body
                    }
                }
            }
        )
        print(response['ResponseMetadata']['HTTPHeaders']['date'], response['MessageId'])
        # storing instance data
        instances_db[instance_id] = str(datetime.now())
        requests.put(url, json=instances_db, headers=headers)
    except:
        print('Error sending email')


def main():
    # reading json
    resp = requests.get(url, json=None, headers=headers).json()
    print(resp)
    instances_db = resp['record']
    print(instances_db)
    tags_to_check = ['Enviroment', 'Name']
    for instance in ec2.instances.all():
        instance_tags = [tag['Key'] for tag in instance.tags]
        missing_tags = [tag for tag in tags_to_check if tag not in instance_tags]
        
        if len(missing_tags) > 0:
            instance_id = instance.id
            for tag in instance.tags:
                if tag['Key'] == 'created-by':
                    created_by = tag['Value']
            if instance_id in instances_db:
                time_now = datetime.now()
                # to check if 6 hours have passed
                email_time = datetime.strptime(instances_db[instance_id], "%Y-%m-%d %H:%M:%S.%f")
                if (time_now - email_time).seconds >= 20:
                    terminate_instance([instance_id])
            else:
                send_email(created_by, missing_tags, instance_id, instances_db)


def lambda_handler(event, context):
    main()
