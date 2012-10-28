"""wxPython AppBar frame (primary entry point)"""
from wxappbar import _appbar, winmsgproc, events, grip
import wx

try:
	False, True
except NameError:
	False = 0
	True = 1

class AppBar( wx.Frame ):
	"""A Task/Application bar for Win32 systems

	Operations:
		CreateVerticalPanel/ CreateHorizontalPanel -- override
			and return your top-level panel(s).  Depending on
			the side of the screen on which we are docked, we
			display either self.horizontalPanel or
			self.verticalPanel within the frame.

	Attributes:
		_data -- an _appbar.ApplicationBar instance. This
			ApplicationBar instance does the actual work of
			updating the system to make this window an AppBar.

		dockSide -- string in ('t','b','l','r') determining
			on which side of the screen the AppBar docks.

		docked -- whether currently docked to one of the sides
			of the screen

		dragging -- whether currently dragging

		otherSize -- dimension of the AppBar which is *not*
			auto-determined by the system, i.e. the width of
			the appbar from the edge of the screen to which
			it is docked.

	Eventual Goals:
		Auto-hide functionality
	"""
	_registeredBars = []
	_data = None
	_callback = None
	FORCE_REDOCK_ON_SYSTEM_MESSAGE = 0
	dockSide = 't'
	docked = 0
	dragging = 0
	otherSize = 64
	
	def __init__(
		self, parent=None, id=-1, title="AppBar",
		pos = wx.DefaultPosition, size = wx.DefaultSize,
		style = wx.FRAME_NO_TASKBAR|wx.CLIP_CHILDREN,
		name = "AppBar",
		dockSide = 't',
		dock = 1,
		otherSize = None,
	):
		"""Initialise the AppBar

		parent -- parent window, normally None
		id -- specific ID to assign to window, normally -1
		title -- not normally displayed
		pos -- not normally used for docked appbars
		style -- by default includes flag to not display in
			the system task-bar.
		dockSide -- one of ('t','b','l','r') indicating side to
			which the appbar should dock initially
		dock -- whether to immediately dock
		otherSize -- if specified, provides the docked width of
			the bar, otherwise this is taken from size via a
			SetOtherSize( size ) call.
		"""
		wx.Frame.__init__( self, parent, id, title, pos, size, style, name )
		self.dockSide = dockSide
		if otherSize:
			self.SetOtherSize( otherSize )
		else:
			self.SetOtherSize( size )
		wx.EVT_MOVE(self, self.OnMove )
		wx.EVT_ACTIVATE_APP( self, self.OnActivate )
		wx.EVT_ACTIVATE( self, self.OnActivate )
		self.CreateControls( style )
		if dock:
			self.Dock()
	def SetOtherSize( self, size ):
		"""Given a size, record our appropriate otherSize

		size -- int, long or size, if not int/long, must be able
			to get size[0] or size[1]
		"""
		if isinstance( size, (int,long)):
			self.otherSize = size
		else:
			if self.dockSide in ('l','r'):
				self.otherSize = size[0]
			else:
				self.otherSize = size[1]
		return self.otherSize
	def CreateControls( self, style ):
		"""Create the controls for the AppBar"""
		x,y,w,h = self.CalculateRectangle()
		self.MoveXY(x,y)
		self.SetSize( (w,h) )
		sizer = wx.BoxSizer( wx.VERTICAL )
		self.verticalPanel = self.CreateVerticalPanel( style )
		self.horizontalPanel = self.CreateHorizontalPanel( style )
		sizer.Add( self.horizontalPanel, 1, wx.EXPAND)
		sizer.Add( self.verticalPanel, 1, wx.EXPAND)
		self.SetSizer( sizer )
		self.DisplayPanel()
		self.SetAutoLayout( True )
		self.Layout()
	def DisplayPanel( self, dockSide = None ):
		"""Display the appropriate child panel for the given dockSide"""
		if dockSide is None:
			dockSide = self.dockSide
		if dockSide in ('l','r'):
			sizer = wx.BoxSizer( wx.VERTICAL )
			self.horizontalPanel.Show( False )
			self.verticalPanel.Show( True )
			sizer.Add( self.verticalPanel, 1, wx.EXPAND )
		else:
			sizer = wx.BoxSizer( wx.HORIZONTAL )
			self.verticalPanel.Show( False )
			self.horizontalPanel.Show( True )
			sizer.Add( self.horizontalPanel, 1, wx.EXPAND )
		self.SetSizer( sizer )
		self.Layout()
			
	def CreateVerticalPanel( self, style=0 ):
		"""Create the vertically-oriented child panel"""
		panel = TestGrip( self, -1 )
		panel.InitWindowDrag( self )
		panel.WindowDragBind()
		return panel
	def CreateHorizontalPanel( self, style=0 ):
		"""Create the horizontally-oriented child panel"""
		panel = TestGrip( self, -1 )
		panel.InitWindowDrag( self )
		panel.SetBackgroundColour( 'blue')
		panel.WindowDragBind()
		return panel
		
	def CalculateRectangle( self, dockSide = None ):
		"""Calculate proper pos rectangle for this frame

		This method attempts to determine the screen position
		and width, height values that will position the frame
		against our current dockSide.  It tries to take into
		account the current size of the desktop, any other
		appbars (such as the taskbar) that are running, and
		our own impact on the size of the desktop if we've
		already been docked (i.e. we have already registered
		our appbar area).

		dockSide -- if specified, calculate the rectangle
			for the given side, rather than our current side,
			otherwise defaults to self.dockSide
		"""
		totalX,totalY = (
			wx.SystemSettings_GetMetric( wx.SYS_SCREEN_X ),
			wx.SystemSettings_GetMetric( wx.SYS_SCREEN_Y )
		)
		client = clientX,clientY,clientW,clientH = wx.GetClientDisplayRect()
		taskX,taskY,taskW,taskH = _appbar.taskbarRectangle()
		
		# now, if we're docked on an edge, then our size
		# needs to be subtracted from the client values
		# to get the resulting "real" values
		# Need to keep in mind that we might not be the bottom-
		# most taskbar!
		selfX,selfY = self.GetPositionTuple()
		selfW,selfH = self.GetSizeTuple()
		if self.docked:
			if self.dockSide == 't':
				clientY -= selfH
				clientH += selfH
			elif self.dockSide == 'b':
				clientH += selfH
			elif self.dockSide == 'l':
				clientX -= selfW
				clientW += selfW
			elif self.dockSide == 'r':
				clientW += selfW
			else:
				raise ValueError( """Unrecognised docking side %r, can't calculate rectangle adjustments"""%( dockSide,))
		# okay, now have the values in "normalised" form, calculate
		# the actual rectangles, depending on the side on which we
		# want to draw
		clientX,clientY = max((clientX,0)),max((clientY,0))
		clientW,clientH = min((clientW,totalX)),min((clientH,totalY))
		if dockSide is None:
			dockSide = self.dockSide
		if dockSide == 't':
			return (clientX,clientY,clientW,self.otherSize)
		elif dockSide == 'b':
			return (clientX,clientY+clientH-selfH,clientW,self.otherSize)
		elif dockSide == 'l':
			return (clientX,clientY,self.otherSize,clientH)
		elif dockSide == 'r':
			return (clientX+clientW-selfW,clientY,self.otherSize,clientH)
		else:
			raise ValueError( """Unrecognised docking side %r, can't calculate correct rectangle"""%( dockSide,))

	def Dock( self, side = None ):
		"""Dock the AppFrame on the given side

		side {'l','r','t','b'} -- string indicating
			the side of the screen on which to dock,
			or None to dock on the currently-set side.
		"""
		if side and side != self.dockSide:
			if self.docked:
				self.Undock()
		if self.docked:
			return 0
		self._data = data = _appbar.ApplicationBar()
		# resize to be somewhat appropriate...
		side = side or self.dockSide
		self.dockSide = side
		data.new( self.GetHandle(), edge = side)
		x,y,w,h = self.dockedPosition = data.setPosition( self.CalculateRectangle(dockSide=side) )
		if not self._callback:
			self._callback = winmsgproc.MessageCallback(
				hWnd = self.GetHandle(),
				messageMap = {
					data.uCallbackMessage: self.OnSystemMessage,
				},
			)
		self.docked = 1
		self._registeredBars.append( data )
		self.SetSize( (w,h) )
		self.SetPosition( (x,y) )
		events.send(
			self,
			events.AppBarDockEvent,
			side,
			1, # docking true
			(x,y),
			(w,h),
		)
		
			
	def Undock( self ):
		"""Undock the frame"""
		try:
			if self._data:
				self._data.remove()
			events.send(
				self,
				events.AppBarDockEvent,
				self.dockSide,
				0, # docking false
				self.dockedPosition[:2],
				self.dockedPosition[2:],
			)
		finally:
			try:
				while self._data in self._registeredBars:
					self._registeredBars.remove( self._data )
			finally:
				self.docked = 0
				self._data = None
	def OnSystemMessage( self, hWnd, messageID, wParam, lParam ):
		"""Handle an appbar system message

		These messages come when the windows taskbar
		is moved or resized (or otherwise changed) and
		they have the effect of requiring a resize of
		our taskbar (normally).  Unfortunately, there's
		nothing I can see which tells us whether the
		taskbar is underneath our currently-reserved
		area, so we wind up with a possible overlap
		condition if the taskbar is dragged to our side
		of the screen :( .

		wParam == 3 -- cascade or tile of windows
			ABN_WINDOWARRANGE notification
		wParam == 1 -- position changed for the appbar
			(incl. resize window)
			ABN_POSCHANGED notification
		wParam == 0 -- auto-hide/always-on-top state
			changed for the taskbar
			ABN_STATECHANGE notification
		"""
		if wParam == 1:
			if self.FORCE_REDOCK_ON_SYSTEM_MESSAGE:
				self.Undock()
				self.Dock()
			else:
				self.OnMove()
		events.send(
			self,
			events.AppBarSystemMessageEvent,
			wParam = wParam,
			lParam = lParam,
		)
		

	def OnMove( self, event=None ):
		"""Deal with a request to move the application bar

		Unfortunately, the system sends un-differentiated
		move events when the client area changes, which can
		result in our being moved away from our docked
		position.  We need to catch and ignore those
		situations.  The current approach is too general,
		as it ignores many otherwise useful move events.

		Note:
			This method is also responsible for triggering
			the interactive docking/undocking mechanisms.
		"""
		if self.docked and not self.dragging:
			x,y,w,h = self.CalculateRectangle()
			self.SetPosition( (x,y))
			self.SetSize( (w,h) )
			if self._data:
				self._data.updatePosition( (x,y,w,h) )
	def OnSize( self, event ):
		"""Deal with a request to size the application bar"""
		event.Skip()
		
	def OnActivate(self, event):
		"""Handle application activation"""
		if event.GetActive() and self.docked and self._data:
			self._data.activate()

class TestGrip( grip.Grip, wx.Panel ):
	"""Testing panel for the appbar"""


def _cleanup():
	"""Cleanup function, un-registers registered appbars"""
	for data in AppBar._registeredBars:
		try:
			data.remove( )
		except AssertionError:
			pass
		
if __name__ == "__main__":
	class TestApplication (wx.PySimpleApp):
		def OnInit(self):
			frame = AppBar(wx.None, -1, "test", size = (300,300))
			frame.Show (1)
			self.SetTopWindow(frame)
			return 1
	try:
		app = TestApplication ()
		app.MainLoop()
	finally:
		_cleanup()
