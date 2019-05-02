import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import numpy as np

# data
df = pd.read_csv('agency.csv', header=0)
df.replace('*', '', inplace=True)

blah = df.loc[:, ((df.columns != 'Date') ^ (df.columns != 'AssetClass') ^ (df.columns !='AssetClassSubType'))].apply(pd.to_numeric)
df = pd.concat((df['AssetClass'], df['AssetClassSubType'], blah, df['Date']), axis=1)

agency_trades = df.groupby('Date').sum()
agency_trades = agency_trades[['FNMATradeCount','FHLMCTradeCount', 'GNMATradeCount', 'OtherTradeCount']]

# launch app
app = dash.Dash(__name__)
app.title = 'Agency and Non-Agency Trading'
server = app.server

#build and serve layouts
def serve_layout():
    return html.Div(children=[
        html.H5(children='BLAH'),
        dcc.Dropdown(options=[
            {'label': 'Number of Trades', 'value': 'num_trades'},
            {'label': '$ Amount of Trades', 'value': '$_trades'},
            {'label': 'Unique CUSIPs Traded', 'value': 'unique_trades'}],
        placeholder='Select Trade Type',
        id='type dropdown'),
        dcc.Graph(id='agency trades')
    ])
app.layout = serve_layout

def build_figure():
    return [{
            'data': [
                go.Scatter(
                    x=agency_trades.index,
                    y=agency_trades['FNMATradeCount'].values,
                    name='FNMA',
                    hoverinfo='skip',
                    orientation='v'
                ),
                go.Scatter(
                    x=agency_trades.index,
                    y=agency_trades['FHLMCTradeCount'].values,
                    name='FHLMC',
                    hoverinfo='skip',
                    orientation='v'
                ),
                go.Scatter(
                    x=agency_trades.index,
                    y=agency_trades['GNMATradeCount'].values,
                    name='GNMA',
                    hoverinfo='skip',
                    orientation='v'
                ),
                go.Scatter(
                    x=agency_trades.index,
                    y=agency_trades['OtherTradeCount'].values,
                    name='Other',
                    hoverinfo='skip',
                    orientation='v'
                ),
            ],
            'layout': go.Layout(
                height=600,
                title='Number of Trades',
            )
        }]

@app.callback(
    [Output('agency trades', 'figure')],
    [Input('type dropdown', 'value')]
)
def update_figure(selected_value):
    return build_figure()


if __name__ == '__main__':
    app.run_server(debug=True)