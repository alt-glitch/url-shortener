import os
import json
import logging
import uuid
import boto3

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

def main(event, context):
    LOG.info("EVENT: " + json.dumps(event))

    query_string_params = event['queryStringParameters']
    if query_string_params is not None:
        target_url = query_string_params['targetUrl']
        if target_url is not None:
            return create_short_url(event)
    
    path_parameters = event['pathParameters']
    if path_parameters is not None:
        if path_parameters['proxy'] is not None:
            return read_short_url(event)
    
    return {
        'statusCode': 200,
        'body': 'usage: ?targetUrl=URL'
    }

def create_short_url(event):
    # get dynamodb table from environment
    table_name = os.environ.get('TABLE_NAME')

    # parse the targeturl
    target_url = event['queryStringParameters']['targetUrl']

    # create a unique ID
    id = str(uuid.uuid4())[0:8]

    # create item in dynamodb
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    table.put_item(Item = {
        'id': id,
        'target_url': target_url
    })

    # create redirect url
    url = "https://" \
        + event["requestContext"]["domainName"] \
        + event["requestContext"]["path"] \
        + id

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/plain'},
        'body': "Created URL {}".format(url)
    }


def read_short_url(event):
    # parse redirect ID from path
    id = event['pathParameters']['proxy']

    # get dynamodb table from environment
    table_name = os.environ.get('TABLE_NAME')

    # query for the URL in dynamodb
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    response = table.get_item(Key={'id': id})
    LOG.debug("RESPONSE: " + json.dumps(response))

    item = response.get('Item', None)
    if item is None:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'text/plain'},
            'body': 'No redirect found for ' + id
        }
    
    return {
        'statusCode': 301,
        'headers': {
            'Location': item.get('target_url')
        }
    }
