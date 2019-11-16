import pandas as pd
import threading
import csv
import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import time
from collections import deque
import plotly.graph_objs as go
from datetime import datetime as dt
import operator, collections

EXT_STYLE = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

class Visualizer(threading.Thread):
   # TODO: CONTINOUS REFRESHING
   # TODO: most used resources uses csv_reader time_spent uses pandas use the same if possible. also in other places
   def __init__(self, resource_loc, time_loc):
      threading.Thread.__init__(self)
      self.daemon = True
      self.RESOURCE_LOC = resource_loc
      self.TIME_LOC = time_loc


   def time_spent(self, files):
      res = [0, [], []]
      for file in files:
         if os.path.exists(file) and len(list(csv.reader(open(file, 'r')))) > 1:

            df = pd.read_csv(file)
            df = df[['name', 'time']].groupby('name').sum().reset_index()
            res[0] += df.sum(axis=0, skipna=True)['time']
            res[1] += list(df.name)
            res[2] += list(df.time)
      if res == [0, [], []]:
         return False
      return res

   def resources_used(self, files):
      temp = {}
      for file in files:
         if os.path.exists(file) and len(list(csv.reader(open(file, 'r')))) > 1:
            with open(file, 'r') as file:
               csv_reader = csv.reader(file)
               next(csv_reader)
               for (name, cpu, ram, counter, timestamp) in csv_reader:
                  temp[name] = [round(float(cpu) + float(temp.get(name)[0] if temp.get(name, 'empty') != 'empty' else 0), 2), round(float(ram) + float(temp.get(
                     name)[1] if temp.get(name, 'empty') != 'empty' else 0), 2), int(counter) + int(temp.get(name)[2] if temp.get(name, 'empty') != 'empty' else 0)]
      if temp == {}:
         return False

      data = []
      for key in temp.keys():
         data.append([key, temp[key][0], temp[key][1], temp[key][2]])
      df = pd.DataFrame(data, columns=['name', 'cpu', 'ram', 'counter'])

      df = df.groupby('name').sum().reset_index()
      cpu = df[['name', 'cpu', 'counter']].sort_values(
         'cpu', ascending=False).head(10)
      ram = df[['name', 'ram', 'counter']].sort_values(
         'ram', ascending=False).head(10)
      return [list(cpu.name), [list(cpu.cpu)[i]/list(cpu.counter)[i] for i in range(10)]], [list(ram.name), [list(ram.ram)[i]/list(ram.counter)[i] for i in range(10)]]

   def overtime(self, file):
      """Ovetime network, disk_io, cpu, ram"""
      if not os.path.exists(file) or len(list(csv.reader(open(file, 'r')))) < 1:
         return False
      overtime = {}
      with open(file, 'r') as f:
         csv_reader = csv.reader(f)
         next(csv_reader)
         for (timestamp, netin, netout, diskin, diskout, cpu, ram) in csv_reader:
            overtime[timestamp] = [timestamp, netin,
                                   netout, diskin, diskout, cpu, ram]
      return [key for key in overtime.keys()], [overtime[key][1] for key in overtime.keys()], [overtime[key][2] for key in overtime.keys()], [overtime[key][3] for key in overtime.keys()], [overtime[key][4] for key in overtime.keys()], [overtime[key][5] for key in overtime.keys()], [overtime[key][6] for key in overtime.keys()]

   def overtime_resource(self, file):
      """Total overtime resources usage"""
      if len(list(csv.reader(open(file, 'r')))) < 1:
         return False
      overtime_res = {}
      with open(file, 'r') as f:
         csv_reader = csv.reader(f)
         next(csv_reader)
         for (name, cpu, ram, counter, timestamp) in csv_reader:
            hour = timestamp[11:13]
            if hour not in overtime_res.keys():
               overtime_res[hour] = [0, 0, 0, 0]
            print(overtime_res[hour])
            overtime_res[hour][0] = round(float(cpu) + float(overtime_res.get(hour)[0] if overtime_res.get(hour, 'empty') != 'empty' else 0), 2)
            overtime_res[hour][1] = round(float(ram) + float(overtime_res.get(hour)[1] if overtime_res.get(hour, 'empty') != 'empty' else 0), 2)
            overtime_res[hour][2] = int(counter) + int(overtime_res.get(hour)[2] if overtime_res.get(hour, 'empty') != 'empty' else 0)
            # overtime_res[hour] = [round(float(
               #  cpu) + float(overtime_res.get(hour)[0] if overtime_res.get(hour, 'empty') != 'empty' else 0), 2), round(float(ram) + float(overtime_res.get(hour)[1] if overtime_res.get(hour, 'empty') != 'empty' else 0), 2), int(counter) + int(overtime_res.get(hour)[2] if overtime_res.get(hour, 'empty') != 'empty' else 0), 0]
            overtime_res[hour][3] += 1
      # print(overtime_res)
      overtime_res = collections.OrderedDict(sorted(
          overtime_res.items(), key=operator.itemgetter(0)))
      # print(overtime_res)
      return [key for key in overtime_res.keys()], [overtime_res[key][0]/(overtime_res[key][2]/overtime_res[key][3]) for key in overtime_res.keys()], [overtime_res[key][1]/(overtime_res[key][2]/overtime_res[key][3]) for key in overtime_res.keys()]
      
   def overtime_time(self, file):
      """Overtime time spent on each application"""
      print('time')
      if not os.path.exists(file) or len(list(csv.reader(open(file, 'r')))) < 1:
         return False
      overtime = {}
      print(file, 'file')
      with open(file, 'r') as f:
         csv_reader = csv.reader(f)
         next(csv_reader)
         print(csv_reader)
         for (name, time, timestamp) in csv_reader:
            times = timestamp[11:14] + \
                '00' if int(timestamp[14:16]) < 30 else timestamp[11:14] + '30'
            if name not in overtime.keys():
               overtime[name] = {}
            overtime[name][times] = float(time) + float(overtime[name].get(times) if overtime[name].get(times, 'empty') != 'empty' else 0)
      print(overtime)
      
      ts, tm = [], []
      for key in overtime.keys():
         ts.append([t for t in overtime[key].keys()])
         tm.append([overtime[key][t] for t in overtime[key].keys()])
      return [key for key in overtime.keys()], ts, tm

   def date_data(self, date):
      now = dt.now()
      if date.split(' ')[0] == now.strftime('%Y-%m-%d'):
         res_used = self.resources_used(self.RESOURCE_LOC)

         overt_data = self.overtime('data/overtime.csv')

         ts = self.time_spent(self.TIME_LOC)
         
         if ts == False or res_used == False or overt_data == False:
            return False
         else:
            return ts, res_used, overt_data

      else:
         custom_date = date[:4] + date[5:7] + date[8:10]
         print('cd', custom_date)
         res_used = self.resources_used(
             ['data/daily/resources_' + custom_date + '.csv'])
         ts = self.time_spent(['data/daily/fg_time_' + custom_date + '.csv'])
         ot = self.overtime(f'data/daily/overtime_{custom_date}.csv')

         if ts == False or res_used == False or ot == False:
            return False
         else:
            return ts, res_used, ot

   def all_data(self, date_range):
      #TODO: cpu / 4
      # if len(date_range) == 1:
      #    return self.date_data(date_range)
      # else:
      #    #TODO: 
      return self.date_data(date_range)
