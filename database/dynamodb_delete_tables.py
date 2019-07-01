import pandas as pd
import numpy as np
import dataviz as dv
import plotly.graph_objs as go
import boto3
from boto3.dynamodb.conditions import Key, Attr

try:
    session = boto3.Session(region_name='us-east-1',
                            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])
    dynamodb = session.resource('dynamodb')
except:
    dynamodb = boto3.resource('dynamodb')

startdate = '20180101'


def get_prices(table_name, start_date):
    table = dynamodb.Table('agency_prices_alt')
    response = table.query(
        KeyConditionExpression=Key('AssetID').eq(table_name) & Key('UniqueID').gt(start_date)
    )
    items = response['Items']

    while response.get('LastEvaluatedKey', False):
        response = table.query(
            KeyConditionExpression=Key('AssetID').eq(table_name) & Key('UniqueID').gt(start_date),
            ExclusiveStartKey=response['LastEvaluatedKey'],
        )
        items = items + response['Items']
    return items


df = pd.DataFrame(get_prices('CMO', startdate))
df['Check'] = df['Date'] + df['MortgageType'] + df['Measure'] + df['Agency']
df = df[df['UniqueID'] == df['Check']]
df = df['UniqueID']

table = dynamodb.Table('agency_prices_alt')
for i in df:
    print(i)
    response = table.delete_item(
        Key={
            'AssetID': 'CMO',
            'UniqueID': i
        }
    )