import csv
import unittest

from recorder import Recorder
from visualizer import Visualizer

class TestRecorder(unittest.TestCase):

   def test_write_resource(self):
      with open('test/data/resource.csv', 'w'):
         pass
      rec = Recorder(['name', 'cpu', 'ram', 'counter',
                       'timestamp'], '', '', '', '')
      
      rec.write_resource('test/data/resource.csv',
                          [('ProcessName', 2.31, 3.54, 1, '2012-12-12 10:32:12')])

      with open('test/data/resource.csv', 'r') as f:
         csv_reader = csv.reader(f)
         next(csv_reader)
         self.assertEqual(['ProcessName', '2.31', '3.54', '1', '2012-12-12 10:32:12'], next(csv_reader))

   def test_write_fg_win(self):
      with open('test/data/fg_win.csv', 'w'):
         pass
      rec1 = Recorder('', ['name', 'time', 'timestamp'], '', '', '')

      rec1.write_fg_win('test/data/fg_win.csv',
                            ['PogramName', 32.45, '2012-12-12 10:32:12'])

      with open('test/data/fg_win.csv', 'r') as f:
         csv_reader = csv.reader(f)
         next(csv_reader)
         self.assertEqual(
             ['PogramName', '32.45', '2012-12-12 10:32:12'], next(csv_reader))

   def test_write_overtime_data(self):
      with open('test/data/overtime.csv', 'w'):
         pass
      rec1 = Recorder('', '', ['timestamp', 'netin', 'netout',
                               'diskin', 'diskout', 'cpu', 'ram'], '', '')

      rec1.write_overtime_data('test/data/overtime.csv',
                               ['2019-11-27 23:08:01', 16, 43, 2664, 1794, 31.9, 86.7])

      with open('test/data/overtime.csv', 'r') as f:
         csv_reader = csv.reader(f)
         next(csv_reader)
         self.assertEqual(
             ['2019-11-27 23:08:01', '16', '43', '2664', '1794', '31.9', '86.7'], next(csv_reader))

   def test_transfer_resources(self):
      with open('test/data/from_resource.csv', 'w'):
         pass
      with open('test/data/to_resource.csv', 'w'):
         pass

      rec1 = Recorder(['name', 'cpu', 'ram', 'counter',
                       'timestamp'], '', '', '', '')
      rec1.write_resource('test/data/from_resource.csv',
                               [('ProcessName', 2.31, 3.54, 1, '2012-12-12 10:32:12')])
      rec1.transfer_resources(
          [('test/data/from_resource.csv', 'test/data/to_resource.csv')])

      with open('test/data/to_resource.csv', 'r') as f:
         csv_reader = csv.reader(f)
         next(csv_reader)
         self.assertEqual(
             ['ProcessName', '2.31', '3.54', '1', '2012-12-12 10:32:12'], next(csv_reader))

   def test_transfer_fg_time(self):
      with open('test/data/from_fg_win.csv', 'w'):
         pass
      with open('test/data/to_fg_win.csv', 'w'):
         pass

      rec1 = Recorder('', ['name', 'time', 'timestamp'], '', '', '')
      rec1.write_fg_win('test/data/from_fg_win.csv',
                        ['PogramName', 32.45, '2012-12-12 10:32:12'])
      rec1.transfer_fg_time([('test/data/from_fg_win.csv',
                             'test/data/to_fg_win.csv')])

      with open('test/data/to_fg_win.csv', 'r') as f:
         csv_reader = csv.reader(f)
         next(csv_reader)
         self.assertEqual(
             ['PogramName', '32.45', '2012-12-12 10:32:12'], next(csv_reader))

   def test_transfer_overtime_data(self):
      with open('test/data/from_overtime.csv', 'w'):
         pass
      with open('test/data/to_overtime.csv', 'w'):
         pass

      rec1 = Recorder('', '', ['timestamp', 'netin', 'netout',
                               'diskin', 'diskout', 'cpu', 'ram'], '', '')
      rec1.write_overtime_data('test/data/from_overtime.csv',
                               ['2019-11-27 23:08:01', 16, 43, 2664, 1794, 31.9, 86.7])
      rec1.transfer_overtime_data(
          'test/data/from_overtime.csv', 'test/data/to_overtime.csv')

      with open('test/data/to_overtime.csv', 'r') as f:
         csv_reader = csv.reader(f)
         next(csv_reader)
         self.assertEqual(
             ['2019-11-27 23', '16.0', '43.0', '2664.0', '1794.0', '31.9', '86.7'], next(csv_reader))


class TestVisualizer(unittest.TestCase):
   def test_time_spent(self):
      with open('test/data/display_fg_win.csv', 'w'):
         pass
      rec1 = Recorder('', ['name', 'time', 'timestamp'], '', '', '')

      rec1.write_fg_win('test/data/display_fg_win.csv',
                        ['ProgramName', 32.45, '2012-12-12 10:32:12'])
      rec1.write_fg_win('test/data/display_fg_win.csv',
                        ['ProgramName', 32.45, '2012-12-12 10:32:12'])
      rec1.write_fg_win('test/data/display_fg_win.csv',
                        ['ProgramTwo', 12.10, '2012-12-12 10:32:12'])

      vis1 = Visualizer('','')
      res = vis1.time_spent(['test/data/display_fg_win.csv'])
      self.assertEqual([77.0, ['ProgramName', 'ProgramTwo'], [64.90, 12.10]], res)

   def test_resources_used(self):
      with open('test/data/display_resource.csv', 'w'):
         pass
      rec1 = Recorder(['name', 'cpu', 'ram', 'counter',
                       'timestamp'], '', '', '', '')

      rec1.write_resource('test/data/display_resource.csv',
                          [('ProcessName', 8.88, 3.52, 1, '2012-12-12 10:32:12'), ('ProcessName', 8.88, 3.52, 1, '2012-12-12 10:32:12')])
      rec1.write_resource('test/data/display_resource.csv',
                          [('ProcessName', 8.88, 3.52, 1, '2012-12-12 10:32:12')])
      rec1.write_resource('test/data/display_resource.csv',
                          [('ProcessTwo', 4.04, 5.52, 1, '2012-12-12 10:32:12')])
      rec1.write_resource('test/data/display_resource.csv',
                          [
                             ('ProcessThree', 4.44, 1.11, 1, '2012-12-12 10:32:12'),
                             ('ProcessFour', 4.44, 1.11, 1, '2012-12-12 10:32:12'),
                             ('ProcessFive', 4.44, 1.11, 1, '2012-12-12 10:32:12'),
                             ('ProcessSix', 4.44, 1.11, 1, '2012-12-12 10:32:12'),
                             ('ProcessSeven', 4.44, 1.11, 1, '2012-12-12 10:32:12'),
                             ('ProcessEight', 4.44, 1.11, 1, '2012-12-12 10:32:12'),
                             ('ProcessNine', 4.44, 1.11, 1, '2012-12-12 10:32:12'),
                             ('ProcessTen', 4.44, 1.11, 1, '2012-12-12 10:32:12'),
                             ])
      
      vis1 = Visualizer('','')
      res = vis1.resources_used(['test/data/display_resource.csv'])
      [[cpunames, cpus], [ramnames, rams]] = res

      self.assertListEqual(sorted(cpunames), sorted(['ProcessName', 'ProcessTwo', 'ProcessThree', 'ProcessFour', 'ProcessFive', 'ProcessSix', 'ProcessSeven', 'ProcessEight', 'ProcessNine', 'ProcessTen']))
      self.assertListEqual(sorted(cpus), sorted([2.22, 1.01, 1.11, 1.11, 1.11, 1.11, 1.11, 1.11, 1.11, 1.11]))
      self.assertListEqual(sorted(ramnames), sorted(['ProcessName', 'ProcessTwo', 'ProcessThree', 'ProcessFour', 'ProcessFive', 'ProcessSix', 'ProcessSeven', 'ProcessEight', 'ProcessNine', 'ProcessTen']))
      self.assertListEqual(sorted(rams), sorted([3.52, 5.52, 1.11, 1.11, 1.11, 1.11, 1.11, 1.11, 1.11, 1.11]))

   def test_overtime(self):
      with open('test/data/display_overtime.csv', 'w'):
         pass
      rec1 = Recorder('', '', ['timestamp', 'netin', 'netout',
                               'diskin', 'diskout', 'cpu', 'ram'], '', '')

      rec1.write_overtime_data('test/data/display_overtime.csv',
                               ['2019-11-27 22:08:01', 5, 26, 4547, 1244, 25.9, 68.7])
      rec1.write_overtime_data('test/data/display_overtime.csv',
                               ['2019-11-27 23:08:01', 16, 43, 2664, 1794, 31.9, 86.7])

      vis1 = Visualizer('','')
      res = vis1.overtime('test/data/display_overtime.csv')
      
      self.assertEqual((['2019-11-27 22:08:01', '2019-11-27 23:08:01'],['5','16'],['26','43'],['4547','2664'],['1244','1794'],['25.9','31.9'],['68.7','86.7']), res)

   def test_ovetime_time(self):

      


if __name__ == '__main__':
   unittest.main()


# write_overtime_data
# write_resource
# write_fg_win
# transfer_overtime_data
# transfer_resources
# transfer_fg_time

# time_spent
# resources_used
# overtime
# overtime_time
