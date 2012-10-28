"""Simple demonstration of AppBar operation

This is still pretty crude, just drops an IE window
on the control and calls it a day.
"""
from wxappbar import appbar, grip
from wxoo import compositecontrol
try:
	from wxPython.iewin import *
except ImportError, err:
	from wx.lib import iewin
	wxIEHtmlWin = iewin.IEHtmlWindow
import wx

try:
	False, True
except NameError:
	False = 0
	True = 1

class DemoHorizontal( grip.Grip, compositecontrol.CompositeControl):
	"""Horizontal display for the application bar"""
	def CreateControls( self, style = 0 ):
		"""Creates the sub-controls in the control"""
		sizer = wx.BoxSizer( wx.HORIZONTAL )
		self.html = wxIEHtmlWin(
			self, -1, style = wx.NO_FULL_REPAINT_ON_RESIZE,
			size = (500,64)
		)
		self.html.Navigate( "http://www.vrplumber.com/" )
		sizer.Add( self.html, 1, wx.EXPAND|wx.ALL, 10 )
		self.SetSizer( sizer )
		self.SetAutoLayout( True )
		sizer.Fit( self )
		self.Layout()


class DemoBar( appbar.AppBar ):
	"""Testing version of Demo bar"""
	otherSize = 120
	def CreateVerticalPanel( self, style=0 ):
		"""Create the vertically-oriented child panel"""
		panel = appbar.TestGrip( self, -1 )
		panel.InitWindowDrag( self )
		panel.WindowDragBind()
		return panel
	def CreateHorizontalPanel( self, style=0 ):
		"""Create the horizontally-oriented child panel"""
		panel = DemoHorizontal( self, -1 )
		panel.InitWindowDrag( self )
		panel.WindowDragBind()
		return panel

if __name__ == "__main__":
	class TestApplication (wx.PySimpleApp):
		def OnInit(self):
			frame = DemoBar(None, -1, "test", size = (300,300))
			frame.Show (1)
			self.SetTopWindow(frame)
			return 1
	try:
		app = TestApplication ()
		app.MainLoop()
	finally:
		appbar._cleanup()
