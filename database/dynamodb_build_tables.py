import boto3
import os

session = boto3.Session(region_name='us-east-1',
                        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])
dynamodb = session.resource('dynamodb')

#build tables
def buildAgencyTrades():
    table = dynamodb.create_table(
        TableName='agency_trades',
        KeySchema=[
            {
                'AttributeName': 'AssetID',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'Date',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'AssetID',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'Date',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 2,
            'WriteCapacityUnits': 2
        }
    )


def buildAllPrices():
    table = dynamodb.create_table(
        TableName='agency_prices_alt',
        KeySchema=[
            {
                'AttributeName': 'AssetID',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'UniqueID',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'AssetID',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'UniqueID',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 8,
            'WriteCapacityUnits': 8
        }
    )
