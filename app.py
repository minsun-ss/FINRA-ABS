import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd

# data
df = pd.read_csv('agency.csv', header=0)
df.replace('*', '', inplace=True)

blah = df.loc[:, ((df.columns != 'Date') ^ (df.columns != 'AssetClass') ^ (df.columns !='AssetClassSubType'))].apply(pd.to_numeric)
df = pd.concat((df['AssetClass'], df['AssetClassSubType'], blah, df['Date']), axis=1)
agency_trades = df.groupby('Date').sum()

# launch app
app = dash.Dash(__name__)
app.title = 'Agency and Non-Agency Trading'
server = app.server

#build and serve layouts
def serve_layout():
    return html.Div(children=[
        html.H5(children='Agency and Non-Agency Trading Volumes (FINRA)'),
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
                    {'label': 'Total', 'value': 'TOTAL'},
                    {'label': 'Agency Pass-Through (TBA, STIP, & Rolls)', 'value': 'AGENCY PASS-THRU (TBA, STIP, $ ROLLS)'},
                    {'label': 'Agency Pass-Through (Specified)', 'value': 'AGENCY PASS-THRU (SPECIFIED)'},
                    {'label': 'Agency CMO', 'value': 'AGENCY CMO'}],
                    placeholder='Select Trade Type',
                    id='security type',
                    value='TOTAL'),], className='one-third column'),
            html.Div([
                dcc.Dropdown(options=[
                    {'label': 'Total', 'value': 'TOTAL'},
                    {'label': 'Single Family 15Y', 'value': 'SINGLE FAMILY 15Y'},
                    {'label': 'Single Family 30Y', 'value': 'SINGLE FAMILY 30Y'},
                    {'label': 'Other', 'value': 'OTHER'},
                    {'label': 'Adjustable/Hybrid', 'value': 'ADJUSTABLE/HYBRID'},
                    {'label': 'P&I', 'value': 'P&I'},
                    {'label': 'IO/PO', 'value': 'IO/PO'}],
                    placeholder='Select Trade Type',
                    id='mortgage type',
                    value='TOTAL'),], className='one-third column'),
        ], className='row'),


        dcc.Graph(id='agency trades'),
    ])
app.layout = serve_layout

def build_figure(tradetype, securitytype, mortgagetype,):
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
        chart_title = 'NUMBER OF TRADES, {}, {}'.format(mortgagetype, securitytype)
    elif tradetype == 'trades_$':
        chart_title = '$ TRADING VOLUME, {}, {}'.format(mortgagetype, securitytype)
    elif tradetype == 'trades_unique':
        chart_title = 'UNIQUE CUSIPS TRADED, {}, {}'.format(mortgagetype, securitytype)

    # for those cases where both mortgage type and security type are TOTALS, just eliminate the duplicate
    if mortgagetype == securitytype:
        chart_title = chart_title.replace('TOTAL, TOTAL', 'TOTAL')

    return {
            'data': [
                go.Scatter(
                    x=agency_trades.index,
                    y=tempdf[temp_columns[0]].values,
                    name='FNMA',
                    hoverinfo='skip',
                    orientation='v'
                ),
                go.Scatter(
                    x=agency_trades.index,
                    y=tempdf[temp_columns[1]].values,
                    name='FHLMC',
                    hoverinfo='skip',
                    orientation='v'
                ),
                go.Scatter(
                    x=agency_trades.index,
                    y=tempdf[temp_columns[2]].values,
                    name='GNMA',
                    hoverinfo='skip',
                    orientation='v'
                ),
                go.Scatter(
                    x=agency_trades.index,
                    y=tempdf[temp_columns[3]].values,
                    name='Other',
                    hoverinfo='skip',
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
    #print(selected_trade, selected_security, selected_mortgage)
    return build_figure(selected_trade, selected_security, selected_mortgage)


if __name__ == '__main__':
    app.run_server(debug=True)