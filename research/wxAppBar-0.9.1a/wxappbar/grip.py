"""Dragging "handle" for the appbar"""
from wxoo import windowdrag
import wx

class Grip( windowdrag.WindowDrag ):
	"""Gripping patch for moving the appbar"""
	currentSide = None
	def OnWindowDragMouseMove( self, event ):
		"""Handle a drag of the title bar, moving our parent

		Note: currently this does not adjust for the "real world"
		size of the desktop, so the window can wind up stuck underneath
		the Windows taskbar or similar intrusion onto the desktop.
		"""
		parent = self.GetWindowDragParent()
		if event.Dragging() and parent:
			deltaX, deltaY = self._calculateDeltas(event)
			x,y = event.GetEventObject().ClientToScreen( (event.GetX(), event.GetY()))
			x,y = float(x)/wx.SystemSettings_GetMetric( wx.SYS_SCREEN_X ), float(y)/wx.SystemSettings_GetMetric( wx.SYS_SCREEN_Y )
			side = quadrant( x,y )
			x,y,w,h = parent.CalculateRectangle( side )
			self.currentSide = side
			parent.SetPosition( (x,y) )
			parent.SetSize( (w,h) )
			parent.DisplayPanel( side )
	def _startDrag( self, parent, event ):
		"""Called to actually start the dragging and capture mouse"""
		parent.dragging = 1
		windowdrag.WindowDrag._startDrag( self, parent, event )
	def _endDrag( self, parent, event ):
		"""Called to finish the dragging and un-capture mouse"""
		parent.dragging = 0
		windowdrag.WindowDrag._endDrag( self, parent, event )
		if self.currentSide:
			parent.Dock( self.currentSide )

def quadrant( x,y ):
	"""Convert an x,y fractional coordinate to closest screen-side
	"""
	if x < y:
		# in left or bottom quadrants
		if x < (1.0-y):
			return 'l'
		else:
			return 'b'
	else:
		# in top or right quadrants
		if x < (1.0-y):
			return 't'
		else:
			return 'r'
