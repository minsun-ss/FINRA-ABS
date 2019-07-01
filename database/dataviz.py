import pandas as pd
import numpy as np
import boto3
from boto3.dynamodb.conditions import Key, Attr
import os
from datetime import datetime, timedelta

# helper file for generating all the dataframes used in the visualization from DynamoDB

try:
    session = boto3.Session(region_name='us-east-1',
                            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])
    dynamodb = session.resource('dynamodb')
except:
    dynamodb = boto3.resource('dynamodb')

#start date for the charts (6 months rolling)
startdate = (datetime.now()-timedelta(days=60)).strftime('%Y%m%d')

# helper for price tables
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

def get_trades():
    # this is the dynamodb part
    table = dynamodb.Table('agency_trades')
    response = table.scan(FilterExpression=Attr('Date').gt(startdate))
    items = response['Items']

    # data for all agency trading volumes using amazon dynamodb
    df = pd.DataFrame(items)
    df.replace('*', '', inplace=True)
    df.replace(np.nan, '', inplace=True)
    df[df.columns[4:]] = df[df.columns[4:]].apply(pd.to_numeric)
    df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')
    return df

# data for tba prices
def get_tba_prices():
    dftba = pd.DataFrame(get_prices('TBA', startdate))
    dftba.replace('*', '', inplace=True)
    dftba.replace('0', '', inplace=True)
    dftba.replace('0.0', '', inplace=True)
    dftba['Date'] = pd.to_datetime(dftba['Date'], format='%Y%m%d')
    coupons = ['<=2.5', '3', '3.5', '4', '4.5', '5', '>5.0']
    dftba[coupons] = dftba[coupons].apply(pd.to_numeric)
    dftba = dftba.replace(np.NaN, '')
    return dftba

# data for fixed rate mbs prices
def get_mbs_fixed_prices():

    dfmbsfixed = pd.DataFrame(get_prices('MBSFIXED', startdate))
    dfmbsfixed.replace('*', '', inplace=True)
    dfmbsfixed.replace('0', '', inplace=True)
    dfmbsfixed.replace('0.0', '', inplace=True)
    dfmbsfixed['Date'] = pd.to_datetime(dfmbsfixed['Date'], format='%Y%m%d')
    dfmbsfixed[dfmbsfixed.columns[0:7]] = dfmbsfixed[dfmbsfixed.columns[0:7]].apply(pd.to_numeric)
    dfmbsfixed.replace(np.NaN, '', inplace=True)
    return dfmbsfixed

# data for floating rate mbs prices
def get_mbs_floating_prices():
    dfmbsfloating = pd.DataFrame(get_prices('MBSFLOATING', startdate))
    dfmbsfloating.replace('*', '', inplace=True)
    dfmbsfloating.replace('0', '', inplace=True)
    dfmbsfloating.replace('0.0', '', inplace=True)
    dfmbsfloating['Date'] = pd.to_datetime(dfmbsfloating['Date'], format='%Y%m%d')
    dfmbsfloating[dfmbsfloating.columns[0:5]] = dfmbsfloating[dfmbsfloating.columns[0:5]].apply(pd.to_numeric)
    dfmbsfloating.replace(np.NaN, '', inplace=True)
    return dfmbsfloating

# data and cleanup for cmo prices
def get_cmo_prices():
    # data for cmo prices
    df3 = pd.DataFrame(get_prices('CMO', startdate))
    df3.replace('*', '', inplace=True)
    df3.replace('0', '', inplace=True)
    df3.replace('0.0', '', inplace=True)
    df3['Date'] = pd.to_datetime(df3['Date'], format='%Y%m%d')
    vintages = ['PRE-2009', '2009-2013', '2014-2016', 'POST-2016']
    df3[vintages] = df3[vintages].apply(pd.to_numeric)
    df3 = df3.replace(np.NaN, '')
    return df3




