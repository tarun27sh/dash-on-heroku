import gevent.monkey
gevent.monkey.patch_all()
import dash
from dash.dependencies import Output, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly 
import plotly.graph_objs as go

import psutil as ps
import threading
import time
from platform import platform

from string import *
import os
from subprocess import check_output, STDOUT
import redis

class Data:
    X=[]
    Y1=[0 for x in range(30)]
    Y2=[0 for x in range(30)]
    Y3=[0 for x in range(30)]
    Y4=[0 for x in range(30)]
    Y5=[0 for x in range(30)]
    Y6=[0 for x in range(30)]
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
    initialized = False
    redis_db = 0
    def __init__(self):
        if not PageHits.initialized:
            if os.environ.get('REDISCLOUD_URL') is not None:
                PageHits.redis_db = redis.from_url(os.environ['REDISCLOUD_URL'])
                print('redic-cloud URL - {}'.format(os.environ.get('REDISCLOUD_URL')))
                print('redic-cloud instance - {}'.format(PageHits.redis_db))
                if not PageHits.redis_db:
                    print('init: redis_db not set, exit')
                    exit(0)
                PageHits.initialized = True
                PageHits.redis_db.set('page_hits', 0)
            else:
                    print('init: redis_db not set, exit')
                    exit(0)

    def get_page_hits(self):
        if not PageHits.redis_db:
            print('redis_db not set, exit')
            exit(0)
        ph = int.from_bytes(PageHits.redis_db.get('page_hits'), byteorder = 'little')
        print('ph = {}'.format(ph))
        if not ph:
            print('errorr getting data from redis, exit')
            exit(0)
        print('get_page_hits: {}'.format(ph))
        return ph

    def inc_page_hit(self):
        if not PageHits.redis_db:
            print('redis_db not set, exit')
            exit(0)
        PageHits.redis_db.incr('page_hits')
        print('set_page_hits: {}'.format(self.get_page_hits()))

    def __str__(self):
        return 'Initialized = {}, Hits = {}'.format(PageHits.initialized, self.get_page_hits())

def get_platform():
    return platform()
    

def get_latest_layout():
    hits = PageHits()
    hits.inc_page_hit()
    print('page hits set - {}'.format(hits.get_page_hits()))
    return html.Div(children = 
        [
            html.P(''),
            html.Div([
                      html.H1(children='Heroku Dyno Stats'),
            ]),
            html.P(''),
            html.P(''),
            html.Div([
                      html.H4(children='This is a python web application created using Dash python web framework and deployed on Heroku Dyno (container)'),
                      html.P(className='text-muted',
                             children='Graphs on this page are for heroku dyno where this web application is deployed'),
                ],
            ),
            html.Table(className='table',
                children = 
                [
                    html.Tr( [html.Th('Attribute'), html.Th("Value")] )
                ] +
                [
                    html.Tr( [html.Td('OS'),         html.Td('{}'.format(get_platform()))] ),
                    html.Tr( [html.Td('#CPUs'),      html.Td('{}'.format(ps.cpu_count()))] ),
                    html.Tr( [html.Td('CPU Clock'),  html.Td('{} MHz'.format(int(ps.cpu_freq().current)))] ),
                    html.Tr( [html.Td('RAM'),       html.Td('{} GB'.format(ps.virtual_memory().total >> 30))] ),
                    html.Tr( [html.Td('#processes'), html.Td('{}'.format(len(ps.pids())))] ),
                ]
            ),
            
            html.Div(className="border border-primary",
                      children = [
                          dcc.Graph(
                                    id='my_graph',
                                    animate=True
                          ),
                          dcc.Interval(
                                    id='my_graph_update',
                                    interval=2000 # ms
                          ),
            ]),
            html.Div(className="border border-primary",
                     children = [
                         dcc.Graph(
                                   id='my_graph2',
                                   animate=True
                         ),
                         dcc.Interval(
                                   id='my_graph_update2',
                                   interval=2000 # ms
                         ),
            ]),
            html.Div(className="border border-primary",
                     children = [
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
                      html.Footer(children=[html.A('Tarun Sharma', href='https://www.linkedin.com/in/tarun27sh/')]),
                      html.Footer(children=['page hits : {}'.format(hits.get_page_hits())])
            ]),
        ],
        className='container',
    )
LSOF = '/app/.apt/usr/bin/lsof'
def get_lsof():
    pid = os.getpid()
    if os.path.isfile(LSOF):
        print('lsof found !')
        lsof = (check_output([LSOF, '-i'], stderr=STDOUT)).split('\n')
        for line in lsof:
            print(line)
    else:
        print('lsof not found, searching for lsof')
        for root, dirs, files in os.walk('/'):
            if 'lsof' in files:
                print('Founnd!! - {}'.format(os.path.join(root, name)))



# Dash app init
#app = dash.Dash(threaded=True)
app = dash.Dash(threaded=False)
server = app.server


app.config['suppress_callback_exceptions']=True
app.config['REDISCLOUD_URL'] = redis.from_url('localhost:6379')
app.layout = get_latest_layout
# externnal css
app.scripts.append_script({"external_url": 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js'})
app.css.append_css({"external_url": 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css'})
get_lsof()





# callbacks for dash events
@app.callback(Output('my_graph', 'figure'), 
              events = [Event('my_graph_update', 'interval')])
def my_graph_update ():
    data = Data()
    print('Update called      - ')
    get_lsof()
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
    return {
            'data'  : [scatter_data],
            'layout': go.Layout(
                               title="inet connections (last 30 seconds)",
                               xaxis = {'title' : 'Units: Seconds', 
                                        'range': [min(x_data), 
                                                  max(x_data)]
                                       },
                               yaxis = {'title' : '#connections', 
                                        'range': [0, 
                                                  max(y_conn)]
                                       }
                               )
    }


