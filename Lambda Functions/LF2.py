import json
import boto3
import requests
from requests_aws4auth import AWS4Auth

region = 'us-east-1' 
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

def clearIndices():
    host = 'https://search-photosearch-jv6lpm2yc67iulmuqlsn6c7b34.us-east-1.es.amazonaws.com/photosearch/'
    res = requests.delete(host,auth=awsauth)
    res = json.loads(res.content.decode('utf-8'))
    return res   

def searchIndices():
    host = 'https://search-photosearch-jv6lpm2yc67iulmuqlsn6c7b34.us-east-1.es.amazonaws.com/photosearch/_search?q='
    res = requests.get(host,auth=awsauth)
    res = json.loads(res.content.decode('utf-8'))
    return res

def searchElasticIndex(search):
    print("inside searchElasticIndex function")
    photos = []
    print(search)
    for s in search:
        print(s)
        host = 'https://search-photosearch-jv6lpm2yc67iulmuqlsn6c7b34.us-east-1.es.amazonaws.com/photosearch/_search?q='+s
        print(host)
        res = requests.get(host,auth=awsauth)
        print(res)
        res = json.loads(res.content.decode('utf-8'))
        print(res)
        for item in res["hits"]["hits"]:
            bucket = item["_source"]["bucket"]
            key = item["_source"]["objectKey"]
            photoURL = "https://{0}.s3.amazonaws.com/{1}".format(bucket,key)
            photos.append(photoURL)
    return photos

def prepareForSearch(res):
    print("inside prepareForSearch function")
    photos = []
    if res["slots"]["Word_A"] != None:
        photos.append(res["slots"]["Word_A"])
    if res["slots"]["Word_B"] != None:
        photos.append(res["slots"]["Word_B"])
    return photos

def sendToLex(message):
    print("inside sendToLex function")
    lex = boto3.client('lex-runtime')
    response = lex.post_text(
        botName='HandleQueriesBot',
        botAlias='photos',
        userId='lf1',
        inputText=message)
    print(response)        
    return response
    
def lambda_handler(event, context):
    # TODO implement
    photos = []
    #res = clearIndices() used to clear indexes in ES
    #res = searchIndices() #used to check index
    print("adadasgswdgdfgdf")
    print(event)
    message = event["queryStringParameters"]["q"]
    print(message)
    resFromLex = sendToLex(message)
    search = prepareForSearch(resFromLex)
    print(photos)
    photos = searchElasticIndex(search)
    return {
        'statusCode': 200,
        'headers': {"Access-Control-Allow-Origin":"*","Access-Control-Allow-Methods":"*","Access-Control-Allow-Headers": "*"},
        'body': json.dumps(photos)
    }

