import boto3

dynamodb = boto3.resource('dynamodb')

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
