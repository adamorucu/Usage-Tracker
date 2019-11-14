import dash
import dash_core_components as dcc
import dash_html_components as html
from collections import deque
import plotly.graph_objs as go
from datetime import datetime as dt

import sys, os
import time

from recorder import Recorder
from visualizer import Visualizer
from taskbar import Taskbar

RESOURCE_FIELDS = ['name', 'cpu', 'ram', 'counter', 'timestamp']
FG_TIME_FIELDS = ['name', 'time', 'timestamp']
OVERTIME_FIELDS = ['timestamp', 'netin', 'netout', 'diskin', 'diskout', 'cpu', 'ram']

RESOURCE_LOC = [
    'data/resources.csv', 'data/minutely_resources.csv', 'data/hourly_resources.csv']
TIME_LOC = ['data/fg_time.csv',
            'data/minutely_fg_time.csv', 'data/hourly_fg_time.csv']

EXT_STYLE = ['https://codepen.io/chriddyp/pen/bWLwgP.css']



if __name__ == '__main__':
   try:
      rec = Recorder(RESOURCE_FIELDS, FG_TIME_FIELDS, OVERTIME_FIELDS, RESOURCE_LOC, TIME_LOC)
      rec.start()
      print('Recording started')

      vis = Visualizer(RESOURCE_LOC, TIME_LOC)

      app = dash.Dash(__name__, external_stylesheets=EXT_STYLE)

      # Main Layout
      app.layout = html.Div(children=[
         html.Div([
            html.H2('Usage Tracker')
         ]),
         html.Div([
            html.Div(id='date-picker', children=[
               dcc.DatePickerSingle(
                  id='datepicker',
                  initial_visible_month=dt.now(),
                  date=str(dt.now()),
                  display_format='MMM Do YYYY'
               )
            ]),
            dcc.Dropdown(
               id='date_type',
               options=[
                  {'label': 'Single Date', 'value': 'single'},
                  {'label': 'Multiple Dates', 'value': 'multiple'},
               ],
               value='single',
               clearable=False
            )
         ], style={'columnCount': 2}),
         html.Div(id='time', style={'columnCount': 1}),
         html.Div(id='resource', style={'columnCount': 2}),
         html.Div(id='overtime', style={'columnCount': 3})
      ])

      # # Date Type
      # @app.callback(
      #    [dash.dependencies.Output(
      #         component_id='date-picker', component_property='children')],
      #    [dash.dependencies.Input(component_id='date_type', component_property='value')]
      # )
      # def datetype(date_type):
      #    print('Date Type: ', date_type)
      #    if date_type == 'single':
      #       return dcc.DatePickerSingle(
      #          id='datepicker',
      #          initial_visible_month=dt.now(),
      #          date=str(dt.now()),
      #          display_format='MMM Do YYYY'
      #       )
      #    else:
      #       return dcc.DatePickerRange(
      #          id='datepicker',
      #          end_date=dt.now(),
      #          display_format='MMM Do YYYY',
      #          start_date_placeholder_text='MMM Do YYYY'
      #       )

      # Fill Data
      @app.callback(
         [
            dash.dependencies.Output(
                component_id='time', component_property='children'),
            dash.dependencies.Output(
                component_id='resource', component_property='children'),
            dash.dependencies.Output(
                component_id='overtime', component_property='children'),
         ],
         [dash.dependencies.Input(
                component_id='datepicker', component_property='date')]
      )
      def update(date):
         print('len date', len(date))
         print('date', date)

         timespent, res_used, overt_data = vis.all_data(date)
         total_time, names4times, times = timespent
         [name_cpu, cpu], [name_ram, ram] = res_used
         [ot_timestamp, netin, netout, diskin, diskout, ot_cpu, ot_ram] = overt_data

         time_graphs = []
         resource_graphs = []
         overtime_graphs = []  
         
         time_graphs.append(html.H2('Total Time: ' + str(int(sum(times)/60)) + ' min', style={'textAlign': 'center', 'marginTop': 100}))

         piechart = go.Pie(values=times, labels=names4times, textinfo='label', hole=.3, showlegend=False)
         time_graphs.append(
            dcc.Graph(
               id='time_pie',
               figure={
                  'data': [piechart]
               },
            )
         )

         resource_graphs.append(
            dcc.Graph(
               id='ram',
               figure={'data': [{
                  'x': name_ram,
                  'y': ram,
                  'type': 'bar',
                  'name': 'RAM'
               }],
                   'layout': {'title': 'RAM', 'yaxis': {'title': 'Usage Percentage (%)'}}}
            )
         )

         resource_graphs.append(
             dcc.Graph(
                 id='ram',
                 figure={'data': [{
                     'x': name_cpu,
                     'y': cpu,
                     'type': 'bar',
                     'name': 'CPU'
                 }],
                     'layout': {'title': 'CPU', 'yaxis': {'title': 'Usage Percentage (%)'}}}
             )
         )

         overtime_graphs.append(
            dcc.Graph(
               id='ot_ram_cpu',
               figure={
                  'data': [
                     {'x': ot_timestamp, 'y': ot_ram, 'type': 'blinear', 'name': 'RAM'},
                     {'x': ot_timestamp, 'y': ot_cpu, 'type': 'blinear', 'name': 'CPU'}
                  ],
                   'layout': {'title': 'RAM-CPU', 'yaxis': {'title': 'Usage Percentage (%)'}}
               }
            )
         )

         overtime_graphs.append(
            dcc.Graph(
               id='ot_ram_cpu',
               figure={
                  'data': [
                     {'x': ot_timestamp, 'y': netin, 'type': 'blinear', 'name': 'Download'},
                     {'x': ot_timestamp, 'y': netout, 'type': 'blinear', 'name': 'Upload'}
                  ],
                   'layout': {'title': 'Network', 'yaxis': {'title': 'Read/Write (MB)'}}
               }
            )
         )
         overtime_graphs.append(
            dcc.Graph(
               id='ot_ram_cpu',
               figure={
                  'data': [
                     {'x': ot_timestamp, 'y': diskin, 'type': 'blinear', 'name': 'Write'},
                     {'x': ot_timestamp, 'y': diskout, 'type': 'blinear', 'name': 'Read'}
                  ],
                  'layout': {'title': 'Disk', 'yaxis': {'title': 'Read/Write (MB)'}}
               }
            )
         )

         return time_graphs, resource_graphs, overtime_graphs

      app.run_server(debug=True)

   except KeyboardInterrupt:
      print('BREAK')
      try:
         sys.exit(0)
      except SystemExit:
         os._exit(0)
