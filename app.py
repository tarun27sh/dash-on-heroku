import dash
from dash.dependencies import Output, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly 
import plotly.graph_objs as go

import psutil as ps
X=[0]
Y1=[ps.cpu_percent()]
Y2=[ps.virtual_memory().percent]
Y3=[ps.net_io_counters().bytes_sent]
Y4=[ps.net_io_counters().bytes_recv]
app = dash.Dash()
server = app.server
app.config['suppress_callback_exceptions']=True
app.layout = html.Div(
    [
        dcc.Graph(id='my_graph',
                  animate=True),
        dcc.Interval(
            id='my_graph_update',
            interval=1000), # ms
    ]        
)

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
    Y3.append(ps.net_io_counters().bytes_sent)
    Y3.append(ps.net_io_counters().bytes_recv)


    data1 = go.Scatter(x = X,y = Y1,name = 'CPU',mode = 'lines+markers')
    data2 = go.Scatter(x = X,y = Y2,name = 'Virtual Memory',mode = 'lines+markers')
    data3 = go.Scatter(x = X,y = Y3,name = 'Bytes Sent',mode = 'lines+markers')
    data4 = go.Scatter(x = X,y = Y4,name = 'Bytes Recv',mode = 'lines+markers')
    data = [data1, data2, data3, data4]
    return {
            'data':data,
            'layout':go.Layout(
                               title="CPU, Virtual-Memory overtime",
                               xaxis = {'title' : 'Units: Seconds', 'range': [min(X), max(X)]},
                               yaxis = {                            'range': [min(Y1+Y2+Y3+Y4), max(Y1+Y2+Y3+Y4)]}
                              )
           }                   

if __name__ == '__main__':
    app.run_server(debug=True)