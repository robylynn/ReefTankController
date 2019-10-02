import dash, dash_core_components as dcc, dash_html_components as html, dash_daq as daq

def initialize_frontend():
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    ControllerFrontend = dash.Dash(__name__, external_stylesheets=external_stylesheets)


    ControllerFrontend.layout = html.Div(children=[
        html.H1(children='Hello Dash'),

        html.Div(children='''
            Dash: A web application framework for Python.
        '''),

        dcc.Graph(
            id='example-graph',
            figure={
                'data': [
                    {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                    {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
                ],
                'layout': {
                    'title': 'Dash Data Visualization'
                }
            }
        ),

        daq.BooleanSwitch(
            id='my-daq-booleanswitch',
            on=True
        )
    ])
    return ControllerFrontend