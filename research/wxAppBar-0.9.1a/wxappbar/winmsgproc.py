"""Windows Message Processing Callbacks"""
from ctypes import wintypes
from ctypes import *
user32 = windll.user32
import traceback, sys

GWL_WNDPROC     = -4

# convenient access to functions
SetWindowLong = user32.SetWindowLongA
CallWindowProc = user32.CallWindowProcA
PostMessage = user32.PostMessageA # non-blocking
SendMessage = user32.SendMessageA # blocking

# method signature for a windows message-processing function
WNDPROC = WINFUNCTYPE(c_long, c_int, c_int, c_int, c_int)

class MessageCallback:
	"""Class to provide message-based callback

	Note: you _must_ retain a reference to this object
	as long as you want to continue servicing messages,
	the object will de-register it's callback during
	it's delete method.
	"""
	previousHandler = None
	def __init__( self, hWnd, messageMap=None ):
		"""Initialize the callback structures and bind

		hWnd -- the handle to the hWnd to be serviced
		messageMap -- mapping from messageID:function
			where each function should have the
			signature ( hWnd, messageInteger, wParam, lParam )
		"""
		self.hWnd = hWnd
		self.messageMap = messageMap or {}
		self.bind()

	def messageHandler( self, hWnd, messageInteger, wParam, lParam ):
		"""Handler for windows message to the appbar"""
		try:
			function = self.messageMap.get( messageInteger )
			if function is not None:
				return function( hWnd, messageInteger, wParam, lParam )
			elif self.previousHandler:
				return CallWindowProc(
					self.previousHandler,
					hWnd, messageInteger, wParam, lParam
				)
			else:
				return 0
		except Exception, err:
			try:
				traceback.print_exc()
				sys.stderr.write( """ERR: in Window %s Message Handler for %s, resetting handler"""%(hWnd,messageInteger) )
			except:
				pass
			self.unbind()
			return 0

	def bind( self ):
		"""Bind the message-processing callback"""
		self.previousHandler = SetWindowLong(
			self.hWnd, GWL_WNDPROC,
			WNDPROC(self.messageHandler)
		)
		
	def unbind( self ):
		"""Unbind the message-processing callback"""
		try:
			if self.previousHandler:
				SetWindowLong(
					self.hWnd, GWL_WNDPROC,
					self.previousHandler
				)
		except:
			traceback.print_exc()
			sys.stderr.write( """  Unable to restore previous window message handler!""" )
		try:
			del self.previousHandler
		except:
			pass
	def __del__( self ):
		"""Hook deletion to unbind the window message processor"""
		self.unbind()

