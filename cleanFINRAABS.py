import zipfile
import os
import pandas as pd
import numpy as np

# takes a zip list of FINRA ABS trading files, cleans them up and spits them out into 2 raw CSV files.
directory = os.fsencode('data')

def getTradingVolumes(directory):
    for zfile in os.listdir(directory):
        filename = os.fsdecode(zfile)
        zf = zipfile.ZipFile('data/' + filename)

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
                                 'FHLMCTradeCount', 'FHLMCUniqueID', 'FHLMC$Trades', 'GNMATradeCount', 'GNMAUniqueID',
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

def gettbaprices(directory):
    for zfile in os.listdir(directory):
        filename = os.fsdecode(zfile)
        zf = zipfile.ZipFile('data/' + filename)

        month_list = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
                      'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}

        price_fields = ['AVERAGE PRICE', 'WEIGHTED AVG. PRICE', 'AVG. PRICE BOTTOM 5 TRADES', '2ND QUARTILE PRICE',
                        '3RD QUARTILE PRICE', '4TH QUARTILE PRICE', 'AVG. PRICE TOP 5 TRADES', 'STANDARD DEVIATION',
                        'VOLUME OF TRADES (000\'S)', 'NUMBER OF TRADES']

        # build namelist of specific files I need
        pxtables_list = [i for i in zf.namelist() if 'PXTABLES' in i]

        for trading_day in pxtables_list:
            # get trading day date
            trading_date = trading_day.split('-')[1].replace('.xlsx', '')

            # should i fix trading date?
            trading_date = '{}/{}/{}'.format(trading_date[4:6], trading_date[6:], trading_date[:4])

            # build monthlist:
            current_month = int(trading_date[0:2])
            chart_month_list = {current_month: 'Current Month', (current_month + 1) % 12: 'Current Month + 1',
                                (current_month + 2) % 12: 'Current Month + 2',
                                (current_month + 3) % 12: 'Current Month + 3'}

            # start reading stuff in
            df = pd.read_excel(zf.open(trading_day), sheet_name='TBA', skiprows=8, header=None)
            df[0] = df[1].where(~df[1].isin(price_fields)).fillna(method='ffill')

            # let's slice off the bottom part of this based on when the footnotes start - this is a variable line sheet
            df = df.loc[:df[df[0].str.contains('Indicates')].index.values[0] - 2]

            # let's pull out the settlement dates
            df[9] = df[0].where(df[0].str.contains('Settlement')).fillna(method='ffill')

            df[10] = df[0].where(df[0].str.contains('PRICING TABLE')).fillna(method='ffill')
            new = df[10].str.split(' - ', expand=True)
            df[11] = new[0]
            df[12] = new[1]
            df.drop(10, axis=1, inplace=True)
            df[11] = df[11].str.replace('PRICING TABLE: ', '')
            df = df[~(df[0] == df[1])]
            df.columns = ['Agency', 'Measure', '<=2.5', '3', '3.5', '4', '4.5', '5', '>5.0', 'SettlementMonth',
                          'AssetClassType', 'AssetClassSubType']
            df['SettlementMonth'] = df['SettlementMonth'].str.replace(' Settlement', '')
            df['Date'] = trading_date
            df['SettlementDateChart'] = [chart_month_list[month_list[d]] for d in df['SettlementMonth']]

            # clean up some null stuff
            df = df[~(df['Measure'].isna())]

            # check to see if filepath exists and append headers if they don't
            if os.path.isfile('tbaprices.csv'):
                pass
            else:
                pd.DataFrame(df.columns).transpose().to_csv('tbaprices.csv', header=False, index=False, mode='a')

            df.to_csv('tbaprices.csv', header=False, index=False, mode='a')

gettbaprices(directory)