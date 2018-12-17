import dash
from dash.dependencies import Output, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly 
import plotly.graph_objs as go

import psutil as ps
import threading
import time

class Data:
    X=[]
    Y1=[]
    Y2=[]
    Y3=[]
    Y4=[]
    initialized = False
    connections = 0
    ticks = 0
    def __init__(self):
        # print on UI # of inits called
        Data.connections += 1
        if Data.initialized:
            return
        else:
            Data.X=[0]
            Data.Y1=[ps.cpu_percent()]
            Data.Y2=[ps.virtual_memory().percent]
            Data.Y3=[ps.net_io_counters().bytes_sent >> 20]
            Data.Y4=[ps.net_io_counters().bytes_recv >> 20]
            Data.initialized = True
            Data.ticks=0
            t = threading.Thread(self.every_one_sec_stats())
            t.start()
    
    def every_one_sec_stats(self):
        while True:
            print('1sec ')
            Data.ticks += 1
            Data.X.append( Data.X[-1] + 1 )
            Data.Y1.append(ps.cpu_percent())
            Data.Y2.append(ps.virtual_memory().percent)
            Data.Y3.append(ps.net_io_counters().bytes_sent >> 20)
            Data.Y4.append(ps.net_io_counters().bytes_recv >> 20)
            time.sleep(1)

    def get_timestamp_readings(self):
        return self.X[-30:]

    def get_cpu_percent_readings(self):
        return self.Y1[-30:]

    def get_vmem_percent_readings(self):
        return self.Y2[-30:]

    def get_MB_sent_readings(self):
        return self.Y3[-30:]

    def get_MB_recv_readings(self):
        return self.Y4[-30:]

    def __repr__(self):
        return 'ticks={}, cpu={}, vmem={}, MBout={}, MBin={}'.format(self.ticks, self.Y1, self.Y2, self.Y3, self.Y4)

    def __str__(self):
        return 'ticks={}, cpu={}, vmem={}, MBout={}, MBin={}'.format(self.ticks, self.Y1, self.Y2, self.Y3, self.Y4)

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
                            interval=2000 # ms
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
                            interval=2000 # ms
                  ),
        ])
    ], 
    style={'marginBottom': 50, 'marginTop': 25}
)



@app.callback(Output('my_graph', 'figure'), 
              events = [Event('my_graph_update', 'interval')])
def my_graph_update ():
    data = Data()
    print('Update called      - ')
    scatter_data1 = go.Scatter(x = data.get_timestamp_readings(),
                               y = data.get_cpu_percent_readings(),
                               name = 'CPU',
                               mode = 'lines+markers',
                               fill = 'tozeroy')
    scatter_data2 = go.Scatter(x = data.get_timestamp_readings(), 
                                  y = data.get_vmem_percent_readings(),
                                  name = 'Virtual Memory',
                                  mode = 'lines+markers',
                                  fill = 'tonexty')
    scatter_data = [scatter_data1, scatter_data2]
    return {
            'data'  : scatter_data,
            'layout': go.Layout(
                               title="CPU, Virtual-Memory overtime (Last 30 readings)",
                               xaxis = {'title' : 'Units: Seconds', 'range': [min(data.get_timestamp_readings()), max(data.get_timestamp_readings())]},
                               yaxis = {'title' : '%age'          , 'range': [0, max(data.get_cpu_percent_readings() + data.get_vmem_percent_readings())]}
                               )
           }                   

@app.callback(Output('my_graph2', 'figure'), 
              events = [Event('my_graph_update2', 'interval')])
def my_graph_update2 ():
    data = Data()
    print('Updating 2nd graph - ')
    scatter_data3 = go.Scatter(x = data.get_timestamp_readings(),
                       y = data.get_MB_sent_readings(),
                       name = 'MB Sent',
                       mode = 'lines+markers',
                       fill = 'tozeroy')
    scatter_data4 = go.Scatter(x = data.get_timestamp_readings(),
                       y = data.get_MB_recv_readings(),
                       name = 'MB Recv',
                       mode = 'lines+markers',
                       fill = 'tonexty')
    scatter_data = [scatter_data3, scatter_data4]
    return {
            'data'  : scatter_data,
            'layout': go.Layout(
                               title="Pkt sent/recv overtime (last 30 readings)",
                               xaxis = {'title' : 'Units: Seconds', 'range': [min(data.get_timestamp_readings()), max(data.get_timestamp_readings())]},
                               yaxis = {'title' : 'MB'            , 'range': [0, max(data.get_MB_sent_readings() + data.get_MB_recv_readings())]}
                               )
           }                   
if __name__ == '__main__':
    app.run_server(debug=True)
