import pandas as pd
import numpy as np
import boto3
from boto3.dynamodb.conditions import Key, Attr
import os
from datetime import datetime, timedelta

# helper file for generating all the dataframes used in the visualization from DynamoDB

# Sets up the DynamoDB session
try:
    session = boto3.Session(region_name='us-east-1',
                            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])
    dynamodb = session.resource('dynamodb')
except:
    dynamodb = boto3.resource('dynamodb')

#start date for the charts (uses a 60 day rolling average)
startdate = (datetime.now()-timedelta(days=60)).strftime('%Y%m%d')

def get_prices(table_name, start_date):
    '''
    Pulls all pricee data across all asset categories based on specified start date to current date from DynamoDB.
    
    :param table_name: name of price data table
    :param start_date: Earliest date to pull data from DynamoDB.
    :return: all the database entries beginning from start date to current date of specified price table.
    '''
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
    '''
    Pulls the top level trade volume data across all asset categories based on specified start date to current date
    from DynamoDB.
    :return: dataframe with the trading volume data.
    '''
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

def get_tba_prices():
    '''
    Pulls just TBA prices from the run generated from get_prices(). Cleans it up for general use.
    :return: dataframe with TBA-only data.
    '''
    dftba = pd.DataFrame(get_prices('TBA', startdate))
    dftba.replace('*', '', inplace=True)
    dftba.replace('0', '', inplace=True)
    dftba.replace('0.0', '', inplace=True)
    dftba['Date'] = pd.to_datetime(dftba['Date'], format='%Y%m%d')
    coupons = ['<=2.5', '3', '3.5', '4', '4.5', '5', '>5.0']
    dftba[coupons] = dftba[coupons].apply(pd.to_numeric)
    dftba = dftba.replace(np.NaN, '')
    return dftba

def get_mbs_fixed_prices():
    '''
    Pulls just fixed-rate MBS prices from the run generated from get_prices(). Cleans it up for general use.
    :return:  dataframe with fixed-rate MBS-only data.
    '''

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
    '''
    Pulls just floating-rate MBS prices from the run generated from get_prices(). Cleans it up for general use.
    :return: dataframe with floating-rate MBS-only data.
    '''
    dfmbsfloating = pd.DataFrame(get_prices('MBSFLOATING', startdate))
    dfmbsfloating.replace('*', '', inplace=True)
    dfmbsfloating.replace('0', '', inplace=True)
    dfmbsfloating.replace('0.0', '', inplace=True)
    dfmbsfloating['Date'] = pd.to_datetime(dfmbsfloating['Date'], format='%Y%m%d')
    dfmbsfloating[dfmbsfloating.columns[0:5]] = dfmbsfloating[dfmbsfloating.columns[0:5]].apply(pd.to_numeric)
    dfmbsfloating.replace(np.NaN, '', inplace=True)
    return dfmbsfloating

def get_cmo_prices():
    '''
    Pulls just CMO prices from the run generated from get_prices(). Cleans it up for general use.
    :return: dataframe with CMO-only price data.
    '''
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




