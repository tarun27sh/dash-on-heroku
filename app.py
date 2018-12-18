import dash
from dash.dependencies import Output, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly 
import plotly.graph_objs as go

import psutil as ps
import threading
import time


about = '''
This is a python web application created using Dash python web framework and deployed on Free Heroku Dyno
'''

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
            Data.Y3=[ps.net_io_counters().bytes_sent >> 10]
            Data.Y4=[ps.net_io_counters().bytes_recv >> 10]
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
            Data.Y3.append(ps.net_io_counters().bytes_sent >> 10)
            Data.Y4.append(ps.net_io_counters().bytes_recv >> 10)
            time.sleep(1)

    def get_timestamp_readings(self):
        return self.X[-30:]

    def get_cpu_percent_readings(self):
        return self.Y1[-30:]

    def get_vmem_percent_readings(self):
        return self.Y2[-30:]

    def get_KB_sent_readings(self):
        return self.Y3[-30:]

    def get_KB_recv_readings(self):
        return self.Y4[-30:]

    def __repr__(self):
        return 'ticks={}, cpu={}, vmem={}, KBout={}, KBin={}'.format(self.ticks, self.Y1, self.Y2, self.Y3, self.Y4)

    def __str__(self):
        return 'ticks={}, cpu={}, vmem={}, KBout={}, KBin={}'.format(self.ticks, self.Y1, self.Y2, self.Y3, self.Y4)

class PageHits:
    page_hits = 0
    initialized = False
    def __init__(self):
        if PageHits.initialized:
            return
        else:
            PageHits.page_hits = 0
            PageHits.initialized = True
    def get_page_hits(self):
        PageHits.page_hits += 1
        print('page hits set - {}'.format(PageHits.page_hits))
        return PageHits.page_hits
    def __str__(self):
        return 'Initialized = {}, Hits = {}'.format(PageHits.initialized, PageHits.page_hits)


# externnal css
#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

hits = PageHits()
print('page hits set - {}'.format(hits))
app = dash.Dash()
server = app.server
app.config['suppress_callback_exceptions']=True

def get_latest_layout():
    return html.Div(children = 
        [
            html.Div([
                      html.H1(children='Heroku Dyno System Stats', style={'color': 'blue', 'fontSize': 20, 'font-family': 'Sans-Serif'}),
                      html.H2(children=about, style={'color': 'grey', 'fontSize': 14, 'font-family': 'Sans-Serif'}),
                      html.P(children='No of CPUs       : {}'.format(ps.cpu_count()), 
                             style={'color': 'grey', 'fontSize': 12, 'font-family': 'Sans-Serif'}),
                      html.P(children='CPU Freq         : {}'.format(ps.cpu_freq()),  
                             style={'color': 'grey', 'fontSize': 12, 'font-family': 'Sans-Serif'}),
                      html.P(children='No of connections: {}'.format(len(ps.net_connections())), 
                             style={'color': 'grey', 'fontSize': 12, 'font-family': 'Sans-Serif'}),
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
            ]),
            html.Div([
                      html.P(children='page hits : {}'.format(hits.get_page_hits()),
                             style={'color': 'grey', 'fontSize': 12, 'font-family': 'Sans-Serif'}),
            ]),
        ], 
        style={'marginBottom': 50, 'marginTop': 25}
    )


app.layout = get_latest_layout

@app.callback(Output('my_graph', 'figure'), 
              events = [Event('my_graph_update', 'interval')])
def my_graph_update ():
    data = Data()
    print('Update called      - ')
    x_data = data.get_timestamp_readings()
    y_cpu = data.get_cpu_percent_readings()
    y_vmem = data.get_vmem_percent_readings()
    scatter_data1 = go.Scatter(x = x_data,
                               y = y_cpu,
                               name = 'CPU',
                               mode = 'lines+markers',
                               fill = 'tozeroy')
    scatter_data2 = go.Scatter(x = x_data, 
                               y = y_vmem,
                               name = 'Virtual Memory',
                               mode = 'lines+markers',
                               fill = 'tonexty')
    scatter_data = [scatter_data1, scatter_data2]
    return {
            'data'  : scatter_data,
            'layout': go.Layout(
                               title="CPU, Virtual-Memory overtime (Last 30 readings)",
                               xaxis = {'title' : 'Units: Seconds', 
                                        'range' : [min(x_data), 
                                                   max(x_data)]
                                       },
                               yaxis = {'title' : '%age'          , 
                                        'range' : [min(y_cpu + y_vmem), 
                                                   max(y_cpu + y_vmem)]}
                               )
           }                   

@app.callback(Output('my_graph2', 'figure'), 
              events = [Event('my_graph_update2', 'interval')])
def my_graph_update2 ():
    data = Data()
    print('Updating 2nd graph - ')
    x_data = data.get_timestamp_readings()
    y_recv = data.get_KB_recv_readings()
    y_sent = data.get_KB_sent_readings()
    scatter_data3 = go.Scatter(x = x_data,
                               y = y_sent,
                               name = 'KB Sent',
                               mode = 'lines+markers',
                               fill = 'tozeroy')
    scatter_data4 = go.Scatter(x = x_data,
                               y = y_recv,
                       name = 'KB Recv',
                       mode = 'lines+markers',
                       fill = 'tonexty')
    scatter_data = [scatter_data3, scatter_data4]
    return {
            'data'  : scatter_data,
            'layout': go.Layout(
                               title="Pkt sent/recv overtime (last 30 readings)",
                               xaxis = {'title' : 'Units: Seconds', 
                                        'range': [min(x_data), 
                                                  max(x_data)]},
                               yaxis = {'title' : 'KB'            , 
                                        'range': [min(y_sent + y_recv), 
                                                  max(y_sent + y_recv)]}
                               )
           }                   
