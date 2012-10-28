"""Low-level ctypes extension for application bar interactions

The mechanisms in this module should be compatible
with any Win32 GUI engine, as they merely wrap the
Win32 API.

http://www.thescarms.com/vbasic/appbar.asp

// these are put in the wparam of callback messages
#define ABN_STATECHANGE    0x0000000
#define ABN_POSCHANGED     0x0000001
#define ABN_FULLSCREENAPP  0x0000002
#define ABN_WINDOWARRANGE  0x0000003 // lParam == TRUE means hide

// flags for get state
#define ABS_AUTOHIDE    0x0000001
#define ABS_ALWAYSONTOP 0x0000002

#define ABE_LEFT        0
#define ABE_TOP         1
#define ABE_RIGHT       2
#define ABE_BOTTOM      3

WINSHELLAPI UINT APIENTRY SHAppBarMessage(DWORD dwMessage, PAPPBARDATA pData);

////
////  EndAppBar
////
"""
from ctypes import wintypes
from ctypes import *
shell = windll.shell32
user32 = windll.user32
SHAppBarMessage = shell.SHAppBarMessage

class RECT(wintypes.RECT):
	"""Simple RECT sub-class with repr for debugging

	fields are: left, right, top, bottom
	"""
	def __repr__(self):
		return "RECT {left: %s, top: %s, right: %s, bottom: %s}" % (
			self.left, self.top,
			self.right, self.bottom,
		)

WNDPROC = WINFUNCTYPE(c_long, c_int, c_int, c_int, c_int)

class APPBARDATA( Structure ):
	"""Structure for storing AppBar message information

	typedef struct _AppBarData {
		DWORD cbSize;
		HWND hWnd;
		UINT uCallbackMessage;
		UINT uEdge;
		RECT rc;
		LPARAM lParam;
	} APPBARDATA, *PAPPBARDATA;
	"""
	_fields_ = [
		("cbSize",wintypes.DWORD),
		("hWnd",wintypes.HWND),
		("uCallbackMessage", c_ulong),
		("uEdge", c_ulong),
		("rc", RECT),
		("lParam",wintypes.LPARAM),
	]
	def __repr__(self):
		return """%s { %s }"""%(
			self.__class__.__name__,
			", ".join(
				[ "%s=%r"%(field[0],getattr(self,field[0]))
				  for field in self._fields_
				]
			),
		)
	__str__ = __repr__

PAPPBARDATA = POINTER(APPBARDATA)

def taskbarRectangle():
	"""Retrieve the current windows taskbar rectangle"""
	data = ApplicationBar()
	data._send( data.ABM_GETTASKBARPOS )
	return (
		data.rc.left,
		data.rc.top,
		data.rc.right-data.rc.left,
		data.rc.bottom-data.rc.top,
	)



class ApplicationBar( APPBARDATA ):
	"""Convenience wrapper around APPBARDATA"""
	ABM_NEW             =0x00000000 # register new
	ABM_REMOVE          =0x00000001 # deregister
	ABM_QUERYPOS        =0x00000002 # request system alter rectangle to be "safe"
	ABM_SETPOS          =0x00000003 # Inform system of position (rect may be made "safe")
	ABM_GETSTATE        =0x00000004 # Retrieves the autohide and always-on-top states of the Windows taskbar
	ABM_GETTASKBARPOS   =0x00000005 # Retrieves the bounding rectangle of the Windows taskbar
	ABM_ACTIVATE        =0x00000006 # Notifies the system that an appbar has been activated.
	# lParam == TRUE/FALSE means activate/deactivate
	ABM_GETAUTOHIDEBAR  =0x00000007 # Retrieves the handle to the autohide appbar associated with an edge of the screen
	ABM_SETAUTOHIDEBAR  =0x00000008 # Registers or unregisters an autohide appbar for an edge of the screen
	ABM_WINDOWPOSCHANGED=0x00000009 # Notifies the system when an appbar's position has changed

	ABS_AUTOHIDE    = 0x0000001
	ABS_ALWAYSONTOP = 0x0000002

	ABE_LEFT        = 0
	ABE_TOP         = 1
	ABE_RIGHT       = 2
	ABE_BOTTOM      = 3

	ABN_STATECHANGE    = 0x0000000
	ABN_POSCHANGED     = 0x0000001
	ABN_FULLSCREENAPP  = 0x0000002
	ABN_WINDOWARRANGE  = 0x0000003 # lParam == TRUE means hide

	_registered = 0
	position = (-1,-1)
	edgeMapping = {
		ABE_LEFT: ABE_LEFT,
		ABE_RIGHT: ABE_RIGHT,
		ABE_TOP: ABE_TOP,
		ABE_BOTTOM: ABE_BOTTOM,
		'l': ABE_LEFT,
		'r': ABE_RIGHT,
		't': ABE_TOP,
		'b': ABE_BOTTOM,
	}
	def _translateEdge( self, spec ):
		"""Convert ABE_* constant or short string to ABE_* constant"""
		current = self.edgeMapping.get( spec )
		if current is not None:
			return current
		if type(spec) in (str,unicode):
			current = self.edgeMapping.get( spec = spec.lower()[:1] )
			if current is not None:
				return current
		raise ValueError( "Unrecognised edge specifier %s, valid specs are %s"%(
			spec,
			",".join( self.edgeMapping.keys()),
		))
	def new(
		self, hWnd, message= 2038,
		edge = 't',
	):
		"""Register the application bar with the system
		"""
		self.cbSize = wintypes.DWORD(sizeof(self))
		self.hWnd = wintypes.HWND(hWnd)
		self.uCallbackMessage = message
		self.uEdge = self._translateEdge( edge )
		self._send( self.ABM_NEW )
		self._registered = 1
	def setPosition(
		self, 
		rect=(-1,-1,-1,-1),
	):
		"""Set position of appbar, reserving area of screen

		Return the rectangle suggested by the system
		"""
		assert self._registered, """Attempt to do a setPosition of an unregistered application bar %s"""%(self,)
		(
			self.rc.left,self.rc.top,
			self.rc.right,self.rc.bottom
		) = (
			rect[0], rect[1], rect[0]+rect[2], rect[1]+rect[3],
		)
		self._send( self.ABM_QUERYPOS );
		self._send( self.ABM_SETPOS )
		return (
			self.rc.left,
			self.rc.top,
			self.rc.right-self.rc.left,
			self.rc.bottom-self.rc.top,
		)
	def remove( self ):
		"""Remove this appbar from the system's set"""
		assert self._registered, """Attempt to unregister an unregistered application bar %s"""%(self,)
		result = self._send( self.ABM_REMOVE )
		self._registered = 0
		return result
	def updatePosition (self, rect ):
		"""Inform system of updated position"""
		(
			self.rc.left,self.rc.top,
			self.rc.right,self.rc.bottom
		) = (
			rect[0], rect[1], rect[0]+rect[2], rect[1]+rect[3],
		)
		return self._send( self.ABM_WINDOWPOSCHANGED )
	def activate (self):
		"""Uniform system of application activation"""
		return self._send( self.ABM_ACTIVATE )
	
		
	def _send( self, message ):
		"""Send this Appbar structure as a message to the system"""
		pointer = PAPPBARDATA( self )
		return SHAppBarMessage( message, pointer )
