import clr

clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")

from System.Drawing import Icon
from System.Windows.Forms import (Application, Form, NotifyIcon, FormWindowState, MouseButtons)

class Main(Form):

    def __init__(self):
        self.initNotifyIcon()
        self.Resize += self.ResizeForm

    def initNotifyIcon(self):
        self.notifyIcon = NotifyIcon()
        self.notifyIcon.Icon = Icon("test.ico")
        self.notifyIcon.Visible = False
        self.notifyIcon.MouseDoubleClick += self.DoubleClickOnTrayIcon

    def ResizeForm(self, s, e):
        if self.WindowState == FormWindowState.Minimized:
            self.notifyIcon.Visible = True
            self.Visible = False

    def DoubleClickOnTrayIcon(self, s, e):
        if e.Button == MouseButtons.Left:
            self.Visible = True
            if self.WindowState == FormWindowState.Minimized:
                self.WindowState = FormWindowState.Normal
            self.notifyIcon.Visible = False

if __name__ == "__main__":
    main = Main()
    Application.EnableVisualStyles()
    Application.Run(main)
