import json
import boto3
from botocore.vendored import requests
import time
from requests_aws4auth import AWS4Auth


region = 'us-east-1' 
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
s3 = boto3.client('s3')

def lambda_handler(event, context):

    s3_info = event['Records'][0]['s3']
    bucket_name = s3_info['bucket']['name']
    key_name = s3_info['object']['key']
    
    response = s3.head_object(Bucket=bucket_name, Key=key_name)
    
    #print("head_object : " , response)
    if response["Metadata"]:
        customlabels = response["Metadata"]["customlabels"]
        print("customlabels : ", customlabels)
        customlabels = customlabels.split(',')
        customlabels = list(map(lambda x: x.lower(), customlabels))
    
    client = boto3.client('rekognition','us-east-1')
    pass_object = {'S3Object':{'Bucket':bucket_name,'Name':key_name}}
    resp = client.detect_labels(Image=pass_object)
    label_names = list(map(lambda x:x['Name'],resp['Labels']))

    
    print(label_names)
    
    timestamp =time.time()

    labels = []

    for i in range(len(resp['Labels'])):
        labels.append(resp['Labels'][i]['Name'])
    if response["Metadata"]:
        for cl in customlabels:
            print(cl)
            cl = cl.lower().strip()
            if cl not in label_names:
                labels.append(cl)
    print(labels)
    
    format = {'objectKey':key_name,'bucket':bucket_name,'createdTimestamp':timestamp,'labels':labels}
    
    url = "https://search-photosearch-jv6lpm2yc67iulmuqlsn6c7b34.us-east-1.es.amazonaws.com/photosearch/1"
    
    headers = {"Content-Type": "application/json"}
    
    r = requests.post(url,auth=awsauth, data=json.dumps(format).encode("utf-8"), headers=headers)
    
    print(r.text)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
