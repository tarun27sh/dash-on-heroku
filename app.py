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
This is a python web application created using Dash python web framework and deployed on Heroku Dyno 
'''

class Data:
    X=[]
    Y1=[0 for x in range(30)]
    Y2=[0 for x in range(30)]
    Y3=[0 for x in range(30)]
    Y4=[0 for x in range(30)]
    Y5=[0 for x in range(30)]
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
            Data.Y5=[len(ps.net_connections())]
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
            Data.Y5.append(len(ps.net_connections()))
            time.sleep(1)

    def get_timestamp_readings(self):
        return Data.X[-30:]

    def get_cpu_percent_readings(self):
        return Data.Y1[-30:]

    def get_vmem_percent_readings(self):
        return Data.Y2[-30:]

    def get_KB_sent_readings(self):
        return Data.Y3[-30:]

    def get_KB_recv_readings(self):
        return Data.Y4[-30:]

    def get_inet_connections(self):
        return Data.Y5[-30:]

    def __repr__(self):
        return 'ticks={}, cpu={}, vmem={}, KBout={}, KBin={}, conn={}'.format(self.ticks, self.Y1, self.Y2, self.Y3, self.Y4, self.Y5)

    def __str__(self):
        return 'ticks={}, cpu={}, vmem={}, KBout={}, KBin={}, conn={}'.format(self.ticks, self.Y1, self.Y2, self.Y3, self.Y4, self.Y5)

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
        return PageHits.page_hits

    def inc_page_hit(self):
        PageHits.page_hits += 1

    def __str__(self):
        return 'Initialized = {}, Hits = {}'.format(PageHits.initialized, PageHits.page_hits)



def get_latest_layout():
    hits = PageHits()
    hits.inc_page_hit()
    print('page hits set - {}'.format(hits))
    return html.Div(children = 
        [
            html.Div([
                      html.H1(children='Heroku Dyno System Stats'),
            ]),
            html.Div([
                      html.H3(children=about),
                      html.Ul([
                        html.Li('No of CPUs : {}'.format(ps.cpu_count())),
                        html.Li('CPU Freq   : {} MHz'.format(ps.cpu_freq().current)),
                        html.Li('#processes : {}'.format(len(ps.pids()))),
                      ]),
                      #html.P(children='No of CPUs : {}'.format(ps.cpu_count())), 
                      #html.P(children='CPU Freq   : {} MHz'.format(ps.cpu_freq().current)),
                      #html.P(children='#processes : {}'.format(len(ps.pids()))),
                ],
            ),
            html.Div([
                      dcc.Graph(
                                id='my_graph',
                                animate=True
                      ),
                      dcc.Interval(
                                id='my_graph_update',
                                interval=2000 # ms
                      ),
                ],
            ),
            html.Div([
                      dcc.Graph(
                                id='my_graph3',
                                animate=True
                      ),
                      dcc.Interval(
                                id='my_graph_update3',
                                interval=2000 # ms
                      ),
            ]),
            html.Div([
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
                      html.P(children='page hits : {}'.format(hits.get_page_hits())),
                      html.Footer(children='Created By: Tarun Sharma (tarun27sh@gmail.com)'),
            ]),
        ],
        className='container',
    )


# Dash app init
app = dash.Dash()
server = app.server
app.config['suppress_callback_exceptions']=True
app.layout = get_latest_layout
# externnal css
app.scripts.append_script({"external_url": 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js'})
app.css.append_css({"external_url": 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css'})





# callbacks for dash events
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
                               title="CPU, Virtual-Memory overtime (Last 30 seconds)",
                               xaxis = {'title' : 'Units: Seconds', 
                                        'range' : [min(x_data), 
                                                   max(x_data)]
                                       },
                               yaxis = {'title' : '%age'          , 
                                        'range' : [0, 
                                                   100]
                                       }
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
                               title="Pkt sent/recv overtime (last 30 seconds)",
                               xaxis = {'title' : 'Units: Seconds', 
                                        'range': [min(x_data), 
                                                  max(x_data)]},
                               yaxis = {'title' : 'KB'            , 
                                        'range': [min(y_sent + y_recv), 
                                                  max(y_sent + y_recv)]}
                               )
    }
@app.callback(Output('my_graph3', 'figure'), 
              events = [Event('my_graph_update3', 'interval')])
def my_graph_update3 ():
    data = Data()
    print('Updating 3rd graph - ')
    x_data = data.get_timestamp_readings()
    y_conn = data.get_inet_connections()
    scatter_data = go.Scatter(x = x_data,
                               y = y_conn,
                               name = 'No of connections',
                               mode = 'lines+markers',
                               fill = 'tonexty')
    #scatter_data4 = go.Scatter(x = x_data,
    #                           y = y_recv,
    #                   name = 'KB Recv',
    #                   mode = 'lines+markers',
    #                   fill = 'tonexty')
    #scatter_data = [scatter_data3, scatter_data4]
    return {
            'data'  : [scatter_data],
            'layout': go.Layout(
                               title="inet connections (last 30 seconds)",
                               xaxis = {'title' : 'Units: Seconds', 
                                        'range': [min(x_data), 
                                                  max(x_data)]
                                       },
                               yaxis = {'title' : '#connections', 
                                        'range': [min(y_conn), 
                                                  max(y_conn)]
                                       }
                               )
    }


