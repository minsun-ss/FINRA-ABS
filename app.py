import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd


# launch app
app = dash.Dash(__name__)
app.title = 'bwooo'
server = app.server

def serve_layout():
    return html.Div(children=[
        html.H5(children='BLAH')
    ])

app.layout = serve_layout


if __name__ == '__main__':
    app.run_server(debug=True)