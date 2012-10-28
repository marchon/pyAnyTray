import sys, wx, webbrowser  

ID_ICON_TIMER = wx.NewId()  
OPEN_BROWSER=wx.NewId()  
OPEN_PREFS=wx.NewId()  

class MailTaskBarIcon(wx.TaskBarIcon):  

    def __init__(self, parent):  
        wx.TaskBarIcon.__init__(self)  
        self.parentApp = parent  
        self.noMailIcon = wx.Icon("nomail.png",wx.BITMAP_TYPE_PNG)  
        self.youHaveMailIcon = wx.Icon("mail-message-new.png",wx.BITMAP_TYPE_PNG)  
        self.CreateMenu()  
        self.SetIconImage()  

    def CreateMenu(self):  
        self.Bind(wx.EVT_TASKBAR_RIGHT_UP, self.ShowMenu)  
        self.Bind(wx.EVT_MENU, self.parentApp.OpenBrowser, id=OPEN_BROWSER)  
        self.Bind(wx.EVT_MENU, self.parentApp.OpenPrefs, id=OPEN_PREFS)  
        self.menu=wx.Menu()  
        self.menu.Append(OPEN_BROWSER, "Open Browsers for mail","This will open a new Browser with tabs for each account")  
        self.menu.Append(OPEN_PREFS, "Open Preferences")  
        self.menu.AppendSeparator()  
        self.menu.Append(wx.ID_EXIT, "Close App")  

    def ShowMenu(self,event):  
        self.PopupMenu(self.menu)  

    def SetIconImage(self, mail=False):  
        if mail:  
            self.SetIcon(self.youHaveMailIcon, "You have mail")  
        else:  
            self.SetIcon(self.noMailIcon, "No mail")  

class MailFrame(wx.Frame):  

    def __init__(self, parent, id, title):  
        wx.Frame.__init__(self, parent, -1, title, size = (1, 1),  
            style=wx.FRAME_NO_TASKBAR|wx.NO_FULL_REPAINT_ON_RESIZE)  

        self.tbicon = MailTaskBarIcon(self)  
        self.tbicon.Bind(wx.EVT_MENU, self.exitApp, id=wx.ID_EXIT)   
        self.Show(True)  

    def exitApp(self,event):  
        self.tbicon.RemoveIcon()  
        self.tbicon.Destroy()  
        sys.exit()  

    def OpenBrowser(self,event):  
        webbrowser.open('http://codeboje.de/blog/pages/donate.html')  

    def OpenPrefs(self,event):  
        pass  

#---------------- run the program -----------------------  
def main(argv=None):  
    app = wx.App(False)  
    frame = MailFrame(None, -1, ' ')  
    #frame.Center(wx.BOTH)  
    frame.Show(False)  
    app.MainLoop()  

if __name__ == '__main__':  
    main()
