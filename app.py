import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import numpy as np

# data for trading volumes
df = pd.read_csv('agency.csv', header=0)
df.replace('*', '', inplace=True)
blah = df.loc[:, ((df.columns != 'Date') ^ (df.columns != 'AssetClass') ^ (df.columns !='AssetClassSubType'))].apply(pd.to_numeric)
df = pd.concat((df['AssetClass'], df['AssetClassSubType'], blah, df['Date']), axis=1)
df['Date'] = pd.to_datetime(df['Date'])

# data for prices
df2 = pd.read_csv('tbaprices.csv', header=0)
# get rid of stars, get rid of 0s
df2.replace('*', '', inplace=True)
df2.replace('0', '', inplace=True)
df2['Date'] = pd.to_datetime(df2['Date'])
coupons = ['<=2.5', '3', '3.5', '4', '4.5', '5', '>5.0']
df2[coupons] = df2[coupons].apply(pd.to_numeric)
df2 = df2.replace(np.NaN, '')

# data for cmo prices
df3 = pd.read_csv('agencycmoprices.csv')
df3.replace('*', '', inplace=True)
df3.replace('0', '', inplace=True)
df3['Date'] = pd.to_datetime(df3['Date'])
vintages = ['Pre-2009', '2009-2013', '2014-2016', 'Post-2016']
df3[vintages] = df3[vintages].apply(pd.to_numeric)
df3 = df3.replace(np.NaN, '')

# launch app
app = dash.Dash(__name__)
app.title = 'Agency Trading Volumes and Prices (FINRA)'
server = app.server

#build and serve layouts
def serve_layout():
    return html.Div(children=[
        html.H5(children='Agency Trading Volumes (FINRA) - see www.stuffofminsun.com for more details'),
        html.Div([
            html.Div([
                dcc.Dropdown(options=[
                    {'label': 'Number of Trades', 'value': 'trades_num'},
                    {'label': '$ Amount of Trades', 'value': 'trades_$'},
                    {'label': 'Unique CUSIPs Traded', 'value': 'trades_unique'}],
                    placeholder='Select Trade Type',
                    id='trade type',
                    value='trades_num'),], className='one-third column'),
            html.Div([
                dcc.Dropdown(options=[
                    {'label': 'Trade Total', 'value': 'TOTAL'},
                    {'label': 'Trade Type: Agency Pass-Through (TBA, STIP, & Rolls)', 'value': 'AGENCY PASS-THRU (TBA, STIP, $ ROLLS)'},
                    {'label': 'Trade Type: Agency Pass-Through (Specified)', 'value': 'AGENCY PASS-THRU (SPECIFIED)'},
                    {'label': 'Trade Type: Agency CMO', 'value': 'AGENCY CMO'}],
                    placeholder='Select Trade Type',
                    id='security type',
                    value='TOTAL'),], className='one-third column'),
            html.Div([
                dcc.Dropdown(options=[
                    {'label': 'Total Mortgages', 'value': 'TOTAL'},
                    {'label': 'Mortgage Type: Single Family 15Y', 'value': 'SINGLE FAMILY 15Y'},
                    {'label': 'Mortgage Type: Single Family 30Y', 'value': 'SINGLE FAMILY 30Y'},
                    {'label': 'Mortgage Type: Other', 'value': 'OTHER'},
                    {'label': 'Mortgage Type: Adjustable/Hybrid', 'value': 'ADJUSTABLE/HYBRID'},
                    {'label': 'Mortgage Type: P&I', 'value': 'P&I'},
                    {'label': 'Mortgage Type: IO/PO', 'value': 'IO/PO'}],
                    placeholder='Select Trade Type',
                    id='mortgage type',
                    value='TOTAL'),], className='one-third column'),
        ], className='row'),
        dcc.Graph(id='agency trades'),

        # now start the second pricing chart
        html.H5(children='Agency TBA Prices (FINRA)'),
        html.Div([
            html.Div([
                dcc.Dropdown(options=[
                    {'label': 'Average Price', 'value': 'AVERAGE PRICE'},
                    {'label': 'Weighted Average Price', 'value': 'WEIGHTED AVG. PRICE'},
                    {'label': 'Average Price, Bottom 5 Trades', 'value': 'AVG. PRICE BOTTOM 5 TRADES'},
                    {'label': 'Average Price, Top 5 Trades', 'value': 'AVG. PRICE TOP 5 TRADES'},
                    {'label': '2nd Quartile Price', 'value': '2ND QUARTILE PRICE'},
                    {'label': '3rd Quartile Price', 'value': '3RD QUARTILE PRICE'},
                    {'label': '4th Quartile Price', 'value': '4TH QUARTILE PRICE'},
                    {'label': 'Standard Deviation', 'value': 'STANDARD DEVIATION'},
                    {'label': "Volume of Trades (Thousands)", 'value': "VOLUME OF TRADES (000'S)"},
                    {'label': 'Number of Trades', 'value': 'NUMBER OF TRADES'}],
                    placeholder='Select Measure',
                    id='select tba measure',
                    value='AVERAGE PRICE'),
            ], className='three columns'),
            html.Div([
                dcc.Dropdown(options=[
                    {'label': 'Mortgage: Single Family 15Y', 'value': 'SINGLE FAMILY 15Y'},
                    {'label': 'Mortgage: Single Family 30Y', 'value': 'SINGLE FAMILY 30Y'},],
                    placeholder='Select Asset Subtype',
                    id='select asset class subtype',
                    value='SINGLE FAMILY 30Y'),
            ], className='three columns'),
            html.Div([
                dcc.Dropdown(options=[
                    {'label': 'Coupon: <=2.5', 'value': '<=2.5'},
                    {'label': 'Coupon: 3', 'value': '3'},
                    {'label': 'Coupon: 3.5', 'value': '3.5'},
                    {'label': 'Coupon: 4', 'value': '4'},
                    {'label': 'Coupon: 4.5', 'value': '4.5'},
                    {'label': 'Coupon: 5.0', 'value': '5'},
                    {'label': 'Coupon: >5.0', 'value': '>5.0'}, ],
                    placeholder='Select Asset Subtype',
                    id='select coupon type',
                    value='3.5'),
            ], className='three columns'),
            html.Div([
                dcc.Dropdown(options=[
                    {'label': 'Settlement Date: Current Month', 'value': 'Current Month'},
                    {'label': 'Settlement Date: Current Month + 1', 'value': 'Current Month + 1'},
                    {'label': 'Settlement Date: Current Month + 2', 'value': 'Current Month + 2'},
                    {'label': 'Settlement Date: Current Month + 3', 'value': 'Current Month + 3'}, ],
                    placeholder='Select Settlement Month',
                    id='select settlement month',
                    value='Current Month + 1'),
            ], className='three columns'),
        ], className='row'),
        dcc.Graph(id='agency tba prices'),

        # now start the agency CMO pricing chart
        html.H5(children='Agency CMO Prices (FINRA)'),
        html.Div([
            html.Div([
                dcc.Dropdown(options=[
                    {'label': 'Average Price', 'value': 'AVERAGE PRICE'},
                    {'label': 'Weighted Average Price', 'value': 'WEIGHTED AVG. PRICE'},
                    {'label': 'Average Price, Bottom 5 Trades', 'value': 'AVG. PRICE BOTTOM 5 TRADES'},
                    {'label': 'Average Price, Top 5 Trades', 'value': 'AVG. PRICE TOP 5 TRADES'},
                    {'label': '2nd Quartile Price', 'value': '2ND QUARTILE PRICE'},
                    {'label': '3rd Quartile Price', 'value': '3RD QUARTILE PRICE'},
                    {'label': '4th Quartile Price', 'value': '4TH QUARTILE PRICE'},
                    {'label': 'Standard Deviation', 'value': 'STANDARD DEVIATION'},
                    {'label': "Volume of Trades (Thousands)", 'value': "VOLUME OF TRADES (000'S)"},
                    {'label': 'Number of Trades', 'value': 'NUMBER OF TRADES'}],
                    placeholder='Select Agency CMO Measure',
                    id='select cmo measure',
                    value='AVERAGE PRICE'),
            ], className='three columns'),
            html.Div([
                dcc.Dropdown(options=[
                    {'label': 'N/A', 'value': 'TOTAL'}],
                    placeholder='Select Agency CMO Measure Subtype',
                    id='select cmo measure subtype',
                    value='TOTAL'),
            ], className='three columns'),
            html.Div([
                dcc.Dropdown(options=[
                    {'label': 'Mortgage Type: Agency CMO P&I', 'value': 'AGENCY CMO P&I'},
                    {'label': 'Mortgage Type: Agency CMO IO/PO', 'value': 'AGENCY CMO IO/PO'},],
                    placeholder='Select Agency CMO Measure Subtype',
                    id='select cmo mortgage',
                    value='AGENCY CMO P&I'),
            ], className='three columns'),
            html.Div([
                dcc.Dropdown(options=[
                    {'label': 'Vintage: Pre-2009', 'value': 'Pre-2009'},
                    {'label': 'Vintage: 2009-2013', 'value': '2009-2013'},
                    {'label': 'Vintage: 2014-2016', 'value': '2014-2016'},
                    {'label': 'Vintage: Post-2016', 'value': 'Post-2016'},],
                    placeholder='Select Agency CMO Measure Subtype',
                    id='select cmo vintage',
                    value='Post-2016'),
            ], className='three columns'),
        ], className='row'),
        dcc.Graph(id='agency cmo prices'),
    ])
app.layout = serve_layout

def build_main_figure(tradetype, securitytype, mortgagetype, ):
    # build temp df (starting backwards with mortgage type
    tempdf = df
    if mortgagetype == 'TOTAL': pass
    else:
        tempdf = df[df['AssetClassSubType'] == mortgagetype]

    # now build based on security type
    if securitytype == 'TOTAL': pass
    else:
        tempdf = tempdf[tempdf['AssetClass'] == securitytype]
    tempdf = tempdf.groupby('Date').sum()

    # now build based on trade type
    temp_columns = []
    if tradetype == 'trades_num':
        temp_columns = ['FNMATradeCount', 'FHLMCTradeCount', 'GNMATradeCount', 'OtherTradeCount']
    elif tradetype == 'trades_$':
        temp_columns = ['FNMA$Trades', 'FHLMC$Trades', 'GNMA$Trades', 'Other$Trades']
    elif tradetype == 'trades_unique':
        temp_columns = ['FNMAUniqueID', 'FHLMCUniqueID', 'GNMAUniqueID', 'OtherUniqueID']

    # now build the title
    if tradetype == 'trades_num':
        chart_title = 'NUMBER OF TRADES, {}, {}'.format(securitytype, mortgagetype)
    elif tradetype == 'trades_$':
        chart_title = '$ TRADING VOLUME, {}, {}'.format(securitytype, mortgagetype)
    elif tradetype == 'trades_unique':
        chart_title = 'UNIQUE CUSIPS TRADED, {}, {}'.format(securitytype, mortgagetype)

    # for those cases where both mortgage type and security type are TOTALS, just eliminate the duplicate
    if mortgagetype == securitytype:
        chart_title = chart_title.replace('TOTAL, TOTAL', 'TOTAL')


    return {
            'data': [
                go.Scatter(
                    x=tempdf.index,
                    y=tempdf[temp_columns[0]].values,
                    name='FNMA',
                    orientation='v'
                ),
                go.Scatter(
                    x=tempdf.index,
                    y=tempdf[temp_columns[1]].values,
                    name='FHLMC',
                    orientation='v'
                ),
                go.Scatter(
                    x=tempdf.index,
                    y=tempdf[temp_columns[2]].values,
                    name='GNMA',
                    orientation='v'
                ),
                go.Scatter(
                    x=tempdf.index,
                    y=tempdf[temp_columns[3]].values,
                    name='Other',
                    orientation='v'
                ),
            ],
            'layout': go.Layout(
                height=600,
                title=chart_title,
            )
        }


def build_tba_price_figure(selected_measure, selected_asset_class_subtype, selected_coupon_type, selected_settlement_month):
    test = df2[df2['Measure'] == 'AVERAGE PRICE']
    test = test[test['AssetClassSubType'] == 'SINGLE FAMILY 30Y']
    test = test[test['SettlementDateChart'] == 'Current Month']

    # let's start with measure:
    temp = df2[df2['Measure'] == selected_measure]
    temp = temp[temp['AssetClassSubType'] == selected_asset_class_subtype]
    temp = temp[temp['SettlementDateChart'] == selected_settlement_month]
    temp = temp.set_index(['Date', 'Agency']).unstack(level=1)[selected_coupon_type]

    # let's build title
    chart_title = '{}, {}, {}, Settlement Date: {}'.format(selected_measure, selected_asset_class_subtype, selected_coupon_type,
                                          selected_settlement_month)

    return {
            'data': [
                go.Scatter(
                    x=temp.index,
                    y=temp['FNMA'].values,
                    name='FNMA',
                    orientation='v'
                ),
                go.Scatter(
                    x=temp.index,
                    y=temp['FNMA/UMBS'].values,
                    name='FNMA/UMBS',
                    orientation='v'
                ),
                go.Scatter(
                    x=temp.index,
                    y=temp['FHLMC'].values,
                    name='FHLMC',
                    orientation='v'
                ),
                go.Scatter(
                    x=temp.index,
                    y=temp['GNMA'].values,
                    name='GNMA',
                    orientation='v'
                ),
            ],
            'layout': go.Layout(
                height=600,
                title=chart_title,
            )
        }

def build_cmo_price_figure(cmo_measure, cmo_measure2, cmo_mortgage, cmo_vintage):

    # dealing with those situations where the callback dropdown has a measure2 that hasn't updated yet
    if (cmo_measure == "VOLUME OF TRADES (000'S)") ^ (cmo_measure == "NUMBER OF TRADES"): pass
    else: cmo_measure2 = 'TOTAL'

    #building the dataframe
    temp = df3[df3['Measure'] == cmo_measure]
    temp = temp[temp['Measure2'] == cmo_measure2]
    temp = temp[temp['MortgageType'] == cmo_mortgage]
    temp = temp.set_index(['Date', 'Agency']).unstack(level=1)[cmo_vintage]

    # building the title
    chart_title = '{}, {}, {}, Vintage: {}'.format(cmo_measure, cmo_measure2, cmo_mortgage, cmo_vintage)

    return {
            'data': [
                go.Scatter(
                    x=temp.index,
                    y=temp['FNMA'].values,
                    name='FNMA',
                    orientation='v'
                ),
                go.Scatter(
                    x=temp.index,
                    y=temp['FHLMC'].values,
                    name='FHLMC',
                    orientation='v'
                ),
                go.Scatter(
                    x=temp.index,
                    y=temp['GNMA'].values,
                    name='GNMA',
                    orientation='v'
                ),
            ],
            'layout': go.Layout(
                height=600,
                title=chart_title,
            )
        }

@app.callback(
    Output('agency trades', 'figure'),
    [Input('trade type', 'value'),
     Input('security type', 'value'),
     Input('mortgage type', 'value')]
)
def update_figure(selected_trade, selected_security, selected_mortgage):
    return build_main_figure(selected_trade, selected_security, selected_mortgage)

# callback to the agency TBA dropdowns
@app.callback(
    Output('agency tba prices', 'figure'),
    [Input('select tba measure', 'value'),
     Input('select asset class subtype', 'value'),
     Input('select coupon type', 'value'),
     Input('select settlement month', 'value'),
     ]
)
def update_figure(selected_measure, selected_asset_class_subtype, selected_coupon_type, selected_settlement_month):
    return build_tba_price_figure(selected_measure, selected_asset_class_subtype, selected_coupon_type,
                                  selected_settlement_month)

@app.callback(
    [Output('select cmo measure subtype', 'options'),
     Output('agency cmo prices', 'figure'),
     ],
    [Input('select cmo measure', 'value'),
     Input('select cmo measure subtype', 'value'),
     Input('select cmo mortgage', 'value'),
     Input('select cmo vintage', 'value')]
)
def update_dropdown(selected_cmo_measure, selected_cmo_measure_subtype, selected_cmo_mortgage, selected_cmo_vintage):
    if (selected_cmo_measure == "VOLUME OF TRADES (000'S)") ^ (selected_cmo_measure == 'NUMBER OF TRADES'):
        return [{'label': 'Total', 'value': 'TOTAL'},
                {'label': 'Customer Buy', 'value': 'CUSTOMER BUY'},
                {'label': 'Customer Sell', 'value': 'CUSTOMER SELL'},
                {'label': '<= $1MM', 'value': '<= $1MM'},
                {'label': '<= $10MM', 'value': '<= $10MM'},
                {'label': '<= $100MM', 'value': '<= $100MM'},
                {'label': '> $100MM', 'value': '> $100MM'},
                ], build_cmo_price_figure(selected_cmo_measure, selected_cmo_measure_subtype,
                                          selected_cmo_mortgage, selected_cmo_vintage)
    else:
        return [{'label': 'Total', 'value': 'TOTAL'}], build_cmo_price_figure(selected_cmo_measure,
                                                                              selected_cmo_measure_subtype,
                                                                              selected_cmo_mortgage,
                                                                              selected_cmo_vintage)




if __name__ == '__main__':
    app.run_server(debug=True)