import zipfile
import os
import pandas as pd
import numpy as np

# takes a zip list of FINRA ABS trading files, cleans them up and spits them out into 2 raw CSV files.
directory = os.fsencode('data')

for zfile in os.listdir(directory):
    filename = os.fsdecode(zfile)
    zf = zipfile.ZipFile('data/' + filename)

    # building dates
    filedate = filename.split('-')[1].split('.')[0]

    # build namelist of specific files I need
    star_list = [i for i in zf.namelist() if 'STAR' in i]

    for trading_day in star_list:
        # get trading day date
        trading_date = trading_day.split('-')[1].replace('.xlsx', '')

        # should i fix trading date?
        trading_date = '{}/{}/{}'.format(trading_date[4:6], trading_date[6:], trading_date[:4])

        # testing on a single file
        df = pd.read_excel(zf.open(trading_day), sheet_name='TradingActivity', skiprows=11,
                           skipfooter=8, header=None)

        # move some headers to the left, fill out NaN
        df[0] = df[1].where(df[2].isna()).fillna(method='ffill')

        # split into agency and non-agency
        agency_df = df[:12].copy()
        nonagency_df = df[16:].copy()

        # agency - filter out excess rows and add columns
        agency_df = agency_df[~(agency_df[0] == agency_df[1])]
        agency_df.columns = ['AssetClass', 'AssetClassSubType', 'FNMATradeCount', 'FNMAUniqueID', 'FNMA$Trades',
                             'FHLMLCTradeCount', 'FHLMCUniqueID', 'FHLMLC$Trades', 'GNMATradeCount', 'GNMAUniqueID',
                             'GNMA$Trades', 'OtherTradeCount', 'OtherUniqueID', 'Other$Trades']

        # agency - add date 
        agency_df['Date'] = trading_date

        # non-agency = filter out excess columns, rename some mistakes
        nonagency_df = nonagency_df[~(nonagency_df[0] == nonagency_df[1])].drop([8, 9, 10, 11, 12, 13], axis=1)
        nonagency_df[0] = nonagency_df[1].where(
            (nonagency_df[1] == 'CBO/CDO/CLO') ^ (nonagency_df[1] == 'OTHER')).fillna(nonagency_df[0])
        nonagency_df.columns = ['AssetClass', 'AssetClass2', 'IGTradeCount', 'IGUniqueID', 'IG$Trades', 'HYTradeCount',
                                'HYUniqueID', 'HY$Trades']

        # non-agency add date and set index
        nonagency_df['Date'] = trading_date
        # nonagency_df.set_index('AssetClass', inplace=True)

        # check to see if filepath exists and append headers if they don't
        if os.path.isfile('agency.csv'):
            pass
        else:
            pd.DataFrame(agency_df.columns).transpose().to_csv('agency.csv', header=False, index=False, mode='a')

        if os.path.isfile('nonagency.csv'):
            pass
        else:
            pd.DataFrame(nonagency_df.columns).transpose().to_csv('nonagency.csv', header=False, index=False, mode='a')

            # otherwise, append the file without  headers
        agency_df.to_csv('agency.csv', header=False, index=False, mode='a')
        nonagency_df.to_csv('nonagency.csv', header=False, index=False, mode='a')