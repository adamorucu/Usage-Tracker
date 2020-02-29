import threading
import psutil
from datetime import datetime
import time
import win32gui, win32process
import csv
import os, sys
import pandas as pd


class Recorder(threading.Thread):
   def __init__(self, resource_fields, fg_time_fields, overtime_fields, resource_loc, time_loc, freq=5, write_freq=60):
      threading.Thread.__init__(self)
      self.daemon = True
      self.freq = freq
      self.write_freq = write_freq
      self.RESOURCE_FIELDS = resource_fields
      self.FG_TIME_FIELDS = fg_time_fields
      self.OVERTIME_FIELDS = overtime_fields
      self.RESOURCE_LOC = resource_loc
      self.TIME_LOC = time_loc
      self.prev_io = []

   def run(self):
      if not os.path.exists('data'):
         os.makedirs('data/daily')

      for loc in self.RESOURCE_LOC + self.TIME_LOC + ['data/last_update.txt'] + ['data/overtime.csv']:
         if not os.path.exists(loc):
            with open(loc, 'w'):
               pass
      print('Directories Created')
      with open('data/last_update.txt', 'r') as updt_read:
         self.update(updt_read.read())

      open_prog = ""
      fg_win_timer = 0.0
      start_time = time.time()
      while True:
         cpus, rams = self.resource_data()
         now = datetime.now()

         resource_data = []
         for proc in cpus.keys():
            resource_data.append((proc, round(cpus[proc], 2), round(rams[proc], 2), 1,  now.strftime("%Y-%m-%d %H:%M:%S")))


         try:
            curr_prog, win_name = self.current_window()
            if curr_prog == open_prog and fg_win_timer < self.write_freq:
               fg_win_timer += time.time() - start_time
               start_time = time.time()
            else:
               if open_prog != '':
                  self.write_fg_win(
                      'data/fg_time.csv', [open_prog, round(fg_win_timer, 2), now.strftime("%Y-%m-%d %H:%M:%S")])
               fg_win_timer = 0.0
               open_prog = curr_prog
         except:
            print('couldnt specify open window')

         # Look if update needed
         try:
            r_last_update = ''
            with open('data/last_update.txt', 'r') as updt_read:
               r_last_update = updt_read.read()
         except:
            print('Couldnt open last_update.txt')

         if r_last_update != str(now.strftime("%Y-%m-%d")) + ' ' + str(now.hour) + ':' + str(now.minute):
            print('Update started')
            self.write_resource(self.RESOURCE_LOC[0], resource_data)
            io = self.io_data()
            if self.prev_io != []:
               self.write_overtime_data(
                  'data/overtime.csv', [now.strftime("%Y-%m-%d %H:%M:%S")] + [int(io[i] - self.prev_io[i]) for i in range(4)] + [io[4], io[5]])
            print(io)
            self.prev_io = io
            self.update(r_last_update)

         time.sleep(self.freq)


   def update(self, last_update):
      """Gets as input last update time and if it has has changed then transfers all the data to correct files and updates the date file"""
      # when program is closed and opened the next day everything is not transfered to day!!
      now = datetime.now()
      if last_update[:10] != now.strftime("%Y-%m-%d"):
         print('Day changed')
         date = last_update[:10].replace('-', '')
         self.transfer_resources([(self.RESOURCE_LOC[0], self.RESOURCE_LOC[1]), (self.RESOURCE_LOC[1],
                                                                  self.RESOURCE_LOC[2]), (self.RESOURCE_LOC[2], f'data/daily/resources_{ date }.csv')])
         self.transfer_fg_time([(self.TIME_LOC[0], self.TIME_LOC[1]), (self.TIME_LOC[1],
                                                                self.TIME_LOC[2]), (self.TIME_LOC[2], f'data/daily/fg_time_{ date }.csv')])
         self.transfer_overtime_data('data/overtime.csv', f'data/daily/overtime_{date}.csv')
      elif last_update[:13] != now.strftime("%Y-%m-%d %H"):
         print('Hour Changed', last_update[:13], now.strftime("%Y-%m-%d %H"))
         self.transfer_resources([(self.RESOURCE_LOC[0], self.RESOURCE_LOC[1]),
                           (self.RESOURCE_LOC[1], self.RESOURCE_LOC[2])])
         self.transfer_fg_time([(self.TIME_LOC[0], self.TIME_LOC[1]),
                           (self.TIME_LOC[1], self.TIME_LOC[2])])
      else:
         print('Minute changed')
         self.transfer_resources(
            [(self.RESOURCE_LOC[0], self.RESOURCE_LOC[1])])
         self.transfer_fg_time([(self.TIME_LOC[0], self.TIME_LOC[1])])

      with open('data/last_update.txt', 'w+') as w_last_update:
         w_last_update.write(str(now.strftime("%Y-%m-%d")) +
                           ' ' + str(now.hour) + ':' + str(now.minute))

   def current_window(self):
      """Returns Name of currently open window"""
      windowname = win32gui.GetWindowText(win32gui.GetForegroundWindow())
      pid = win32process.GetWindowThreadProcessId(
          win32gui.GetForegroundWindow())
      return psutil.Process(pid[-1]).name(), windowname

   def resource_data(self):
      """Returns a list of processes and their resource usages"""
      cpu = {}
      memory = {}
      counter = 0
      for proc in psutil.process_iter():
         proc_data = {}
         counter += 1
         try:
            proc_data['id'] = proc.pid
            proc_data['name'] = proc.name()
            proc_data['cpu'] = proc.cpu_percent()
            proc_data['memory'] = round(proc.memory_percent(), 2)
            
            temp_mem = 0.0
            temp_cpu = 0.0
            if proc_data['name'] in memory.keys():
               temp_mem = memory[proc_data['name']]
               temp_cpu = cpu[proc_data['name']]
            memory[proc_data['name']] = proc_data["memory"] + temp_mem
            cpu[proc_data['name']] = proc_data["cpu"] + temp_cpu

         except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            print('passed', proc.name())
            pass

      return cpu, memory

   def io_data(self):
      net = psutil.net_io_counters()
      neti, neto = net[0]/1000, net[1]/1000
      disk = psutil.disk_io_counters()
      diski, disko = disk[2]/1000, disk[3]/1000
      cpu = psutil.cpu_percent()
      ram = round(psutil.virtual_memory()[2], 2)
      return [neti, neto, diski, disko, cpu, ram]

   def write_overtime_data(self, file_loc, data):
      file_empty = os.stat(file_loc).st_size == 0
      with open(file_loc, 'a', newline='') as file:
         csv_writer = csv.writer(file, delimiter=',')
         if file_empty:
            csv_writer.writerow(self.OVERTIME_FIELDS)
         csv_writer.writerow(data)

   def write_resource(self, file_loc, data):
      """Writes given resource data to provided location"""
      file_empty = os.stat(file_loc).st_size == 0
      with open(file_loc, 'a', newline='') as file:
         csv_writer = csv.writer(file, delimiter=',')
         if file_empty:
            csv_writer.writerow(self.RESOURCE_FIELDS)

         for row in data:
            csv_writer.writerow(row)

   def write_fg_win(self, file_loc, data):
      """Writes given time data to provided location"""
      file_empty = os.stat(file_loc).st_size == 0
      with open(file_loc, 'a', newline='') as file:
         csv_writer = csv.writer(file, delimiter=',')
         if file_empty:
            csv_writer.writerow(self.FG_TIME_FIELDS)

         csv_writer.writerow(data)

   def transfer_overtime_data(self, from_loc, to_loc):
      temp ={}
      if os.stat(from_loc).st_size != 0 and len(list(csv.reader(open(from_loc, 'r')))) > 1:
         with open(from_loc, 'r') as from_file:
            csv_reader = csv.reader(from_file)
            next(csv_reader)
            for (timestamp, netin, netout, diskin, diskout, cpu, ram) in csv_reader:
               name = timestamp[:-6]
               temp[name] = [name, round(float(netin) + float(temp.get(name)[1] if temp.get(name, 'empty') != 'empty' else 0), 2), round(float(netout) + float(temp.get(name)[2] if temp.get(name, 'empty') != 'empty' else 0), 2), round(float(diskin) + float(temp.get(name)[3] if temp.get(name, 'empty') != 'empty' else 0), 2), round(float(diskout) + float(temp.get(name)[4] if temp.get(name, 'empty') != 'empty' else 0), 2), round(float(cpu) + float(temp.get(name)[5] if temp.get(name, 'empty') != 'empty' else 0), 2), round(float(ram) + float(temp.get(name)[6] if temp.get(name, 'empty') != 'empty' else 0), 2)]
            with open(to_loc, 'a', newline='') as into_file:
                  csv_writer = csv.writer(into_file, delimiter=',')
                  if os.stat(to_loc).st_size == 0:
                     csv_writer.writerow(self.OVERTIME_FIELDS)
                  for key in temp.keys():
                     csv_writer.writerow(
                         (temp[key][0], temp[key][1], temp[key][2], temp[key][3], temp[key][4], temp[key][5], temp[key][6]))
            with open(from_loc, 'w') as file:
               pass

            

   def transfer_resources(self, location_pairs):
      """Transfer resource data from one location to another. Input provided in pairs"""
      
      for from_loc, to_loc in location_pairs:
         if os.stat(from_loc).st_size != 0 and len(list(csv.reader(open(from_loc, 'r')))) > 1: #TODO: maybe remove the first statement?
            # if to_loc == 'data/minutely_resources.csv':
            #    timestamp_length = 16
            # elif to_loc == 'data/hourly_resources.csv':
            #    timestamp_length = 13
            # else:
            #    timestamp_length = 10
            temp = {}
            with open(from_loc, 'r') as from_file:
               csv_reader = csv.reader(from_file)
               next(csv_reader)
               for (name, cpu, ram, counter, timestamp) in csv_reader:
                  temp[name] = [round(float(cpu) + float(temp.get(name)[0] if temp.get(name, 'empty') != 'empty' else 0), 2), round(float(ram) + float(temp.get(name)[1] if temp.get(
                     name, 'empty') != 'empty' else 0), 2), int(counter) + int(temp.get(name)[2] if temp.get(name, 'empty') != 'empty' else 0), timestamp]

               with open(to_loc, 'a', newline='') as into_file:
                  csv_writer = csv.writer(into_file, delimiter=',')
                  if os.stat(to_loc).st_size == 0:
                     csv_writer.writerow(self.RESOURCE_FIELDS)
                  for key in temp.keys():
                     csv_writer.writerow(
                        (key, temp[key][0], temp[key][1], temp[key][2], temp[key][3]))
            with open(from_loc, 'w') as file:
               pass

   def transfer_fg_time(self, location_pairs):
      """Transfer time data from one location to another. Input provided in pairs"""

      for from_loc, to_loc in location_pairs:
         if os.stat(from_loc).st_size != 0 and len(list(csv.reader(open(from_loc, 'r')))) > 1:  #TODO: maybe remove the first statement?
            # if to_loc == 'data/minutely_fg_time.csv':
            #    timestamp_length = 16
            # elif to_loc == 'data/hourly_fg_time.csv':
            #    timestamp_length = 13
            # else:
            #    timestamp_length = 10
            temp = {}
            with open(from_loc, 'r') as from_file:
               csv_reader = csv.reader(from_file)
               next(csv_reader)
               for (name, time, timestamp) in csv_reader:
                  temp[name] = [round(float(time) + float(temp.get(name)[0] if temp.get(
                     name, 'empty') != 'empty' else 0), 2), timestamp]

               with open(to_loc, 'a', newline='') as into_file:
                  csv_writer = csv.writer(into_file, delimiter=',')
                  if os.stat(to_loc).st_size == 0:
                     csv_writer.writerow(self.FG_TIME_FIELDS)
                  for key in temp.keys():
                     csv_writer.writerow((key, temp[key][0], temp[key][1]))

            with open(from_loc, 'w') as file:
               pass


if __name__ == '__main__':
   RESOURCE_FIELDS = ['name', 'cpu', 'ram', 'counter', 'timestamp']
   FG_TIME_FIELDS = ['name', 'time', 'timestamp']
   OVERTIME_FIELDS = ['timestamp', 'netin',
                      'netout', 'diskin', 'diskout', 'cpu', 'ram']

   RESOURCE_LOC = [
      'data/resources.csv', 'data/minutely_resources.csv', 'data/hourly_resources.csv']
   TIME_LOC = ['data/fg_time.csv',
               'data/minutely_fg_time.csv', 'data/hourly_fg_time.csv']

   try:
      rec = Recorder(RESOURCE_FIELDS, FG_TIME_FIELDS, OVERTIME_FIELDS, RESOURCE_LOC, TIME_LOC)
      rec.start()

      time.sleep(999999)

   except KeyboardInterrupt:
      print('BREAK')
      try:
         sys.exit(0)
      except SystemExit:
         os._exit(0)
