import dash
from dash.dependencies import Output, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly 
import plotly.graph_objs as go

import psutil as ps

# externnal css
#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)



app = dash.Dash()
server = app.server
app.config['suppress_callback_exceptions']=True
app.layout = html.Div(children = 
    [
        html.Div([
        ]),
        html.Div([
                  html.H1(children='Heroku Dyno System Stats', style={'color': 'blue', 'fontSize': 20, 'font-family': 'Sans-Serif'}),
                  html.P(children='#-CPU : {}'.format(ps.cpu_count())),
                  dcc.Graph(
                            id='my_graph',
                            animate=True
                  ),
                  dcc.Interval(
                            id='my_graph_update',
                            interval=1000 # ms
                  ),
        ]),
        html.Div([
                  #html.H1(children='Heroku dyno packet sent/recv over time'),
                  dcc.Graph(
                            id='my_graph2',
                            animate=True
                  ),
                  dcc.Interval(
                            id='my_graph_update2',
                            interval=1000 # ms
                  ),
        ])
    ], 
    style={'marginBottom': 50, 'marginTop': 25}
)



X=[0]
X2=[0]
Y1=[ps.cpu_percent()]
Y2=[ps.virtual_memory().percent]
Y3=[ps.net_io_counters().bytes_sent >> 20]
Y4=[ps.net_io_counters().bytes_recv >> 20]




@app.callback(Output('my_graph', 'figure'), 
              events = [Event('my_graph_update', 'interval')])
def my_graph_update ():
    global X
    global Y1
    global Y2
    print('Update calleed')
    X.append(X[-1] + 1)
    Y1.append(ps.cpu_percent())
    Y2.append(ps.virtual_memory().percent)


    data1 = go.Scatter(x = X, 
                       y = Y1,
                       name = 'CPU',
                       mode = 'lines+markers',
                       fill = 'tozeroy')
    data2 = go.Scatter(x = X, 
                       y = Y2,
                       name = 'Virtual Memory',
                       mode = 'lines+markers',
                       fill = 'tonexty')
    data = [data1, data2]
    return {
            'data':data,
            'layout':go.Layout(
                               title="CPU, Virtual-Memory overtime",
                               xaxis = {'title' : 'Units: Seconds', 'range': [min(X), max(X)]},
                               yaxis = {'title' : '%age'          , 'range': [0, max(Y1+Y2)]}
                              )
           }                   

@app.callback(Output('my_graph2', 'figure'), 
              events = [Event('my_graph_update2', 'interval')])
def my_graph_update2 ():
    global X2
    global Y3
    global Y4
    print('Update calleed')
    X2.append(X2[-1] + 1)
    Y3.append(ps.net_io_counters().bytes_sent >> 20) # MB
    Y4.append(ps.net_io_counters().bytes_recv >> 20) # MB


    data3 = go.Scatter(x = X2,
                       y = Y3,
                       name = 'MB Sent',
                       mode = 'lines+markers',
                       fill = 'tozeroy')
    data4 = go.Scatter(x = X2,
                       y = Y4,
                       name = 'MB Recv',
                       mode = 'lines+markers',
                       fill = 'tonexty')
    data = [data3, data4]
    return {
            'data':data,
            'layout':go.Layout(
                               title="Pkt sent/recv overtime",
                               xaxis = {'title' : 'Units: Seconds', 'range': [min(X2), max(X2)]},
                               yaxis = {'title' : 'MB'            , 'range': [0, max(Y3+Y4)]}
                              )
           }                   
if __name__ == '__main__':
    app.run_server(debug=True)
