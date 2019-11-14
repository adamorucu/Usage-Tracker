import webbrowser
import win32api
import win32gui
import win32con
import sys
import os
import threading

class Taskbar(threading.Thread):
   def __init__ (self):
      threading.Thread.__init__(self)
      self.daemon = True
      restart_message = win32gui.RegisterWindowMessage('TaskBar Created')
      message_map = {restart_message: self.restart,
                     win32con.WM_DESTROY: self.destroy,
                     win32con.WM_COMMAND: self.command,
                     win32con.WM_USER+20: self.taskbar_notify}

      wc = win32gui.WNDCLASS()
      hinst = wc.hInstance = win32api.GetModuleHandle(None)
      wc.lpszClassName = "Tracker"
      wc.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW
      wc.hCursor = win32api.LoadCursor(0, win32con.IDC_ARROW)
      wc.hbrBackground = win32con.COLOR_WINDOW
      wc.lpfnWndProc = message_map  # could also specify a wndproc

      # Don't blow up if class already registered to make testing easier
      try:
         classAtom = win32gui.RegisterClass(wc)
      except win32gui.error:
         raise

      # Create the Window.
      style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
      self.hwnd = win32gui.CreateWindow(wc.lpszClassName, "Taskbar Demo", style,
                                          0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT,
                                          0, 0, hinst, None)
      win32gui.UpdateWindow(self.hwnd)
      self.create_icon()
      win32gui.PumpMessages()

   def run(self):
      print('taskbar started')

   def create_icon(self):
      # Try and find a custom icon
        hinst = win32api.GetModuleHandle(None)
        iconPathName = os.path.abspath(
            os.path.dirname(os.path.realpath(__file__)) + "\\images\\pyc.ico")
        if os.path.isfile(iconPathName):
            icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
            hicon = win32gui.LoadImage(
                hinst, iconPathName, win32con.IMAGE_ICON, 0, 0, icon_flags)
        else:
            print("Can't find a Python icon file - using default")
            hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)

        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
        nid = (self.hwnd, 0, flags, win32con.WM_USER+20, hicon, "Tracker")
        try:
            win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)
        except win32gui.error:
           print('sum error')

   def restart(self, hwnd, msg, wparam, lparam):
      self.create_icon()

   def destroy(self, hwnd, msg, wparam, lparam):
      nid = (self.hwnd, 0)
      win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
      win32gui.PostQuitMessage(0)  # Terminate the app.

   def taskbar_notify(self, hwnd, msg, wparam, lparam):
      if lparam == win32con.WM_LBUTTONUP:
         print("You clicked me.")
      elif lparam == win32con.WM_LBUTTONDBLCLK:
         print("You double-clicked me - goodbye")
         win32gui.DestroyWindow(self.hwnd)
         sys.exit()
      elif lparam == win32con.WM_RBUTTONUP:
         print("You right clicked me.")
         menu = win32gui.CreatePopupMenu()
         win32gui.AppendMenu(menu, win32con.MF_STRING, 1023, "Dashboard")
         # win32gui.AppendMenu( menu, win32con.MF_STRING, 1024, "Say Hello")
         win32gui.AppendMenu(menu, win32con.MF_STRING, 1024, "Exit program")
         pos = win32gui.GetCursorPos()
         # See http://msdn.microsoft.com/library/default.asp?url=/library/en-us/winui/menus_0hdi.asp
         win32gui.SetForegroundWindow(self.hwnd)
         win32gui.TrackPopupMenu(
             menu, win32con.TPM_LEFTALIGN, pos[0], pos[1], 0, self.hwnd, None)
         win32gui.PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)
         sys.exit()
      return 1

   def command(self, hwnd, msg, wparam, lparam):
      id = win32api.LOWORD(wparam)
      if id == 1023:
         webbrowser.open('http://127.0.0.1:8050')
      elif id == 1024:
         win32gui.DestroyWindow(self.hwnd)
      else:
         print("Unknown command -", id)
