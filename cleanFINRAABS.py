import zipfile
import os
import pandas as pd
import numpy as np

# takes a zip list of FINRA ABS trading files, cleans them up and spits them out into 2 raw CSV files.
directory = os.fsencode('data')

def get_trading_volumes(directory):
    for zfile in os.listdir(directory):
        filename = os.fsdecode(zfile)
        zf = zipfile.ZipFile('data/' + filename)

        # build namelist of specific files I need
        star_list = [i for i in zf.namelist() if 'STAR' in i]

        for trading_day in star_list:
            # get trading day date
            trading_date = trading_day.split('-')[1].replace('.xlsx', '')

            # should i fix trading date?
            trading_date = '{}{}{}'.format(trading_date[:4], trading_date[4:6], trading_date[6:])

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

def get_tba_prices(directory):
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
            trading_date = '{}{}{}'.format(trading_date[:4], trading_date[4:6], trading_date[6:])

            # build monthlist:
            current_month = int(trading_date[4:6])
            current_month_plus_one = (current_month + 1) % 12
            current_month_plus_two = (current_month + 2) % 12
            current_month_plus_three = (current_month + 3) % 12
            if current_month_plus_one == 0:
                current_month_plus_one = 12
            elif current_month_plus_two == 0:
                current_month_plus_two = 12
            elif current_month_plus_three == 0:
                current_month_plus_three = 12
            chart_month_list = {current_month: 'Current Month', current_month_plus_one: 'Current Month + 1',
                                current_month_plus_two: 'Current Month + 2',
                                current_month_plus_three: 'Current Month + 3'}

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


def get_agency_cmo_prices(directory):
    for zfile in os.listdir(directory):
        filename = os.fsdecode(zfile)
        zf = zipfile.ZipFile('data/' + filename)

        price_fields = ['AVERAGE PRICE', 'WEIGHTED AVG. PRICE', 'AVG. PRICE BOTTOM 5 TRADES', '2ND QUARTILE PRICE',
                        '3RD QUARTILE PRICE', '4TH QUARTILE PRICE', 'AVG. PRICE TOP 5 TRADES', 'STANDARD DEVIATION',
                        'VOLUME OF TRADES (000\'S)', 'NUMBER OF TRADES']

        price_fields_subcategory = ['CUSTOMER BUY', 'CUSTOMER SELL', 'DEALER TO DEALER', '<= $1MM', '<= $10MM',
                                    '<= $100MM', '> $100MM']

        # build namelist of specific files I need
        pxtables_list = [i for i in zf.namelist() if 'PXTABLES' in i]

        for trading_day in pxtables_list:
            # get trading day date
            trading_date = trading_day.split('-')[1].replace('.xlsx', '')

            # should i fix trading date?
            trading_date = '{}{}{}'.format(trading_date[:4], trading_date[4:6], trading_date[6:])

            # build monthlist:
            current_month = int(trading_date[4:6])
            chart_month_list = {current_month: 'Current Month', (current_month + 1) % 12: 'Current Month + 1',
                                (current_month + 2) % 12: 'Current Month + 2',
                                (current_month + 3) % 12: 'Current Month + 3'}

            # start reading stuff in
            df = pd.read_excel(zf.open(trading_day), sheet_name='AgencyCMO', skiprows=8, header=None)

            df.replace(np.NaN, '', inplace=True)
            df = df.loc[:df[df[1].str.contains('Indicates')].index.values[0] - 2]
            df[0] = df[1].where(df[1].isin(price_fields)).fillna(method='ffill')

            df[6] = df[1].where(df[1].isin(price_fields_subcategory))
            df[7] = df[1].where(~((df[1].isin(price_fields) ^ (df[1].isin(price_fields_subcategory))))).fillna(
                method='ffill')
            df[8] = df[1].where(df[1].str.contains('PRICING TABLE')).fillna(method='ffill')

            # future proofing just a bit by not hard coding the vintage years.
            vintage_years = df.loc[2, [2, 3, 4, 5]].values
            df = df[~(df[1] == df[7])]
            df.drop(1, axis=1, inplace=True)
            df[8] = df[8].str.replace('PRICING TABLE: ', '')
            df[8] = df[8].str.replace(' - BY DEAL VINTAGE', '')
            df.columns = ['Measure', vintage_years[0], vintage_years[1], vintage_years[2], vintage_years[3], 'Measure2',
                          'Agency',
                          'MortgageType']
            df.Measure2 = df.Measure2.fillna('TOTAL')
            df['Date'] = trading_date

            # check to see if filepath exists and append headers if they don't
            if os.path.isfile('agencycmoprices.csv'):
                pass
            else:
                pd.DataFrame(df.columns).transpose().to_csv('agencycmoprices.csv', header=False, index=False, mode='a')

            df.to_csv('agencycmoprices.csv', header=False, index=False, mode='a')

def get_agency_mbs_prices(directory):
    for zfile in os.listdir(directory):
        filename = os.fsdecode(zfile)
        zf = zipfile.ZipFile('data/' + filename)

        # build namelist of specific files I need
        star_list = [i for i in zf.namelist() if 'PXTABLES' in i]

        price_fields = ['AVERAGE PRICE', 'WEIGHTED AVG. PRICE', 'AVG. PRICE BOTTOM 5 TRADES', '2ND QUARTILE PRICE',
                        '3RD QUARTILE PRICE', '4TH QUARTILE PRICE', 'AVG. PRICE TOP 5 TRADES', 'STANDARD DEVIATION',
                        'VOLUME OF TRADES (000\'S)', 'NUMBER OF TRADES']

        for trading_day in star_list:
            # get trading day date
            trading_date = trading_day.split('-')[1].replace('.xlsx', '')

            # should i fix trading date?
            trading_date = '{}{}{}'.format(trading_date[:4], trading_date[4:6], trading_date[6:])

            # testing on a single file
            df = pd.read_excel(zf.open(trading_day), sheet_name='MBS', skiprows=8, header=None)
            df.replace(np.NaN, '', inplace=True)
            df = df.loc[:df[df[1].str.contains('Indicates')].index.values[0] - 2]
            df[0] = df[1].where(df[1].str.contains('PRICING TABLE')).fillna(method='ffill')
            df[0] = df[0].str.replace('PRICING TABLE: AGENCY PASS-THRU \(SPECIFIED\) - ', '')

            df[9] = df[1].where(df[1].isin(price_fields))
            df[10] = df[1].where(df[9].isna()).fillna(method='ffill')

            # split the df in 2
            df1 = df[~(df[0] == 'ARMS/HYBRIDS')].drop(1, axis=1).copy()
            df2 = df[df[0] == 'ARMS/HYBRIDS'].copy()

            df1.columns = df1[df1[9].isna() & ~(df1[8] == '')].iloc[0]
            df1.columns.values[0], df1.columns.values[8], df1.columns.values[9] = 'Mortgage Type', 'Measure', 'Agency'
            df1 = df1[~(df1['Measure'].isna())]
            df1['Date'] = trading_date

            df2.drop([1, 7, 8], axis=1, inplace=True)
            df2.columns = df2[df2[9].isna() & ~(df2[6] == '')].iloc[0]
            df2.columns.values[0], df2.columns.values[6], df2.columns.values[7] = 'Mortgage Type', 'Measure', 'Agency'
            df2 = df2[~(df2['Measure'].isna())]
            df2['Date'] = trading_date

            # check to see if filepath exists and append headers if they don't
            if os.path.isfile('mbspricesfixed.csv'):
                pass
            else:
                pd.DataFrame(df1.columns).transpose().to_csv('mbspricesfixed.csv', header=False, index=False, mode='a')

            if os.path.isfile('mbspricesfloating.csv'):
                pass
            else:
                pd.DataFrame(df2.columns).transpose().to_csv('mbspricesfloating.csv', header=False, index=False,
                                                             mode='a')

                # otherwise, append the file without  headers
            df1.to_csv('mbspricesfixed.csv', header=False, index=False, mode='a')
            df2.to_csv('mbspricesfloating.csv', header=False, index=False, mode='a')

get_tba_prices(directory)