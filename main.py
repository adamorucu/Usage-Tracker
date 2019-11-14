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
      print('rec started')

      vis = Visualizer(RESOURCE_LOC, TIME_LOC)
      # vis.start()
      print('vis started')

      # Create Taskbar icon
    #   tsk = Taskbar()
    #   tsk.start()

      app = dash.Dash(__name__, external_stylesheets=EXT_STYLE)

      # Main layout
      app.layout = html.Div(children=[
          html.Div([
              html.H2('Usage Tracker')
          ]),
          dcc.DatePickerSingle(
              id='input-day',
              initial_visible_month=dt.now(),
              date=str(dt.now()),
              display_format='MMM Do YYYY'
          ),
          html.H4(id='total-time'),
          html.Div(id='times', style={'columnCount': 1}),
          html.Div(id='resources', style={'columnCount': 2})
      ])

      @app.callback(
          [dash.dependencies.Output(component_id='total-time', component_property='children'),
           dash.dependencies.Output(component_id='times', component_property='children'),
           dash.dependencies.Output(component_id='resources', component_property='children')],
          [dash.dependencies.Input(
              component_id='input-day', component_property='date')]
      )
      def update(date):
         now = dt.now()
         if date.split(' ')[0] == now.strftime('%Y-%m-%d'):
            [name_cpu, cpu], [name_ram, ram] = vis.resources_used(vis.RESOURCE_LOC)
            print(vis.overtime('data/overtime.csv')[:2])
            [ot_timestamp, netin, netout, diskin, diskout, cpuot, ramot] = vis.overtime('data/overtime.csv')
            cpu = [c/4 for c in cpu]
            ts = vis.time_spent(vis.TIME_LOC)
            if ts != False:
               total, names, times = ts
            else:
               total, names, times = 0, ['No Data'], [1]

         else:
            form_date = date[:4] + date[5:7] + date[8:10]
            [ot_timestamp, netin, netout, diskin, diskout,
             cpu, ram] = vis.overtime(f'data/daily/overtime_{form_date}.csv')
            mostr = vis.resources_used(
                ['data/daily/resources_' + form_date + '.csv'])
            ts = vis.time_spent(['data/daily/fg_time_' + form_date + '.csv'])
            vis.overtime_time('data/daily/fg_time_' + form_date + '.csv')
            if mostr == False or ts == False:
               return html.H2('No Data Available', style={'textAlign': 'center', 'marginTop': 100}), html.H2('')
            else:
               [name_cpu, cpu], [name_ram, ram] = mostr
               total, names, times = ts

         res_graphs = []
         time_graphs = []
         piechart = go.Pie(values=times, labels=names,
                           textinfo='label', hole=.3, showlegend=False)
         
         totaltime = html.H2('Total Time: ' + str(int(sum(times)/60)) + ' min', style={
                             'textAlign': 'center', 'marginTop': 100})
         
         time_graphs.append(
             dcc.Graph(
                 id='time',
                 figure={
                     'data': [piechart]
                 },
             )
         )
        #  print(sum(cpu))
         res_graphs.append(dcc.Graph(
             id='ram',
             figure={
                'data': [
                    {'x': name_ram, 'y': ram, 'type': 'bar', 'name': 'RAM'}
                ],
                 'layout': {
                    'title': 'RAM',
                }
             }
         ))
         res_graphs.append(dcc.Graph(
             id='cpu',
             figure={
                'data': [
                    {'x': name_cpu, 'y': cpu, 'type': 'bar', 'name': 'CPU'}
                ],
                 'layout': {
                    'title': 'CPU',
                }
             }
         ))
        #  res_graphs.append(dcc.Graph(
        #      id='ot',
        #      figure={
        #         'data': [
        #             {'x': ot_timestamp, 'y': netin, 'type': 'bar', 'name': 'CPU'}
        #         ],
        #          'layout': {
        #             'title': 'NET in ',
        #         }
        #      }
        #  ))
         res_graphs.append(dcc.Graph(
             id='ot',
             figure={
                'data': [
                    {'x': ot_timestamp, 'y': ramot, 'type': 'blinear', 'name': 'CPU'}
                ],
                 'layout': {
                    'title': 'ram ot ',
                }
             }
         ))
         res_graphs.append(dcc.Graph(
             id='ot',
             figure={
                'data': [
                    {'x': ot_timestamp, 'y': cpuot, 'type': 'line', 'name': 'CPU'}
                ],
                 'layout': {
                    'title': 'cpu ot ',
                }
             }
         ))




        #  if date.split(' ')[0] != now.strftime('%Y-%m-%d'):
        #      ots = vis.overtime_resource(
        #          'data/daily/resources_' + form_date + '.csv')
        #     #  print(ots)
        #      if ots != False:
        #          times, cpus, rams = ots
        #          res_graphs.append(dcc.Graph(
        #             id='ram',
        #             figure={
        #                 'data': [
        #                     {'x': times, 'y': rams, 'type': 'bar', 'name': 'RAM'}
        #                 ],
        #                 'layout': {
        #                     'title': 'RAM',
        #                 }
        #             }
        #          ))
        #          res_graphs.append(dcc.Graph(
        #             id='cpu',
        #             figure={
        #                 'data': [
        #                     {'x': times, 'y': cpus, 'type': 'bar', 'name': 'CPU'}
        #                 ],
        #                 'layout': {
        #                     'title': 'CPU',
        #                 }
        #             }
        #          ))

         return totaltime, time_graphs, res_graphs

      app.run_server(debug=True)


   except KeyboardInterrupt:
      print('BREAK')
      try:
         sys.exit(0)
      except SystemExit:
         os._exit(0)
