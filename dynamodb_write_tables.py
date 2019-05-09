import boto3
import pandas as pd

session = boto3.Session(region_name='us-east-1',
                        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])
dynamodb = session.resource('dynamodb')

def writeAllTrades():
    # opens the csv files and appends them to the Dynamo trade table
    print('Writing extracted agency trades to Amazon DynamoDB...')
    table = dynamodb.Table('agency_trades')
    table.meta.client.get_waiter('table_exists').wait(TableName='agency_trades')
    df = pd.read_csv('csv/tradingvolumes_agency.csv', header=0)
    df['AssetID'] = df['AssetClass'] + df['AssetClassSubType']
    for i in df.columns: df[i] = df[i].astype(str)
    stream = df.T.to_dict().values()
    for i in stream:
       print(i)
       table.put_item(Item=i)

def writeAllPrices():
    # opens the csv files and appends them to the Dynamo price table
    print('Writing extracted agency prices to Amazon DynamoDB...')
    table = dynamodb.Table('agency_prices_alt')
    table.meta.client.get_waiter('table_exists').wait(TableName='agency_prices_alt')

    # tba
    df = pd.read_csv('csv/prices_tba.csv', header=0)
    for i in df.columns:
        df[i] = df[i].astype(str)
    df['AssetID'] = 'TBA'
    df['UniqueID'] = df['Date'] + df['AssetClassType'] + df['AssetClassSubType'] + df['Measure'] + df['SettlementMonth'] + df['Agency']
    stream = df.T.to_dict().values()
    for i in stream:
        print(i)
        table.put_item(Item=i)

    # cmo
    df = pd.read_csv('csv/prices_cmo.csv', header=0)
    for i in df.columns: df[i] = df[i].astype(str)
    df['AssetID'] = 'CMO'
    df['UniqueID'] = df['Date'] + df['MortgageType'] + df['Measure'] + df['Agency']
    stream = df.T.to_dict().values()
    for i in stream:
        print(i)
        table.put_item(Item=i)

    # mbs fixed
    df = pd.read_csv('csv/prices_mbsfixed.csv', header=0)
    for i in df.columns: df[i] = df[i].astype(str)
    df['AssetID'] = 'MBSFIXED'
    df['UniqueID'] = df['Date'] + df['Mortgage Type'] + df['Measure'] + df['Measure2'] + df['Agency']
    stream = df.T.to_dict().values()
    for i in stream:
        print(i)
        table.put_item(Item=i)

    # mbs floating
    df = pd.read_csv('prices_mbsfloating.csv', header=0)
    for i in df.columns: df[i] = df[i].astype(str)
    df['AssetID'] = 'MBSFLOATING'
    df['UniqueID'] = df['Date'] + df['Mortgage Type'] + df['Measure'] + df['Agency']
    stream = df.T.to_dict().values()
    for i in stream:
        print(i)
        table.put_item(Item=i)
