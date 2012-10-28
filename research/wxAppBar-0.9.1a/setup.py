#!/usr/bin/env python
"""Installs wxAppBar using distutils

Run:
	python setup.py install
to install the package from the source archive.
"""

if __name__ == "__main__":
	import sys,os, string
	from distutils.sysconfig import *
	from distutils.core import setup,Extension
	from distutils.command.build_ext import build_ext
	from distutils.command.install import install
	from distutils.command.install_data import install_data
	##from my_install_data import *

	##############
	## Following is from Pete Shinners,
	## apparently it will work around the reported bug on
	## some unix machines where the data files are copied
	## to weird locations if the user's configuration options
	## were entered during the wrong phase of the moon :) .
	from distutils.command.install_data import install_data
	class smart_install_data(install_data):
		def run(self):
			#need to change self.install_dir to the library dir
			install_cmd = self.get_finalized_command('install')
			self.install_dir = getattr(install_cmd, 'install_lib')
			# should create the directory if it doesn't exist!!!
			return install_data.run(self)
	##############
	### The following automates the inclusion of files while avoiding problems with UNIX
	### where case sensitivity matters.
	dataFiles = []
	excludedTypes = ('.py','.pyc','.pyo', '.db', '.max','.gz','.bat')
	def nonPythonFile( file ):
		if string.lower( file ) == 'cvs':
			return 0
		else:
			return (os.path.splitext( file )[1]).lower() not in excludedTypes
	dataDirectories = [
		'wxappbar',
	]
	for directory in dataDirectories:
		finalFiles = []
		for file in os.listdir( directory):
			fullFile = os.path.join( directory, file )
			if os.path.isfile(fullFile) and nonPythonFile(fullFile):
				finalFiles.append (os.path.join(directory, file))
		if finalFiles:
			dataFiles.append (
				(os.path.join('resourcepackage',directory),finalFiles)
			)

	from sys import hexversion
	if hexversion >= 0x2030000:
		# work around distutils complaints under Python 2.2.x
		extraArguments = {
			'classifiers': [
				"""License :: OSI Approved :: BSD License""",
				"""Programming Language :: Python""",
				"""Topic :: Software Development :: Libraries :: Python Modules""",
				"""Intended Audience :: Developers""",
				"""Topic :: Desktop Environment""",
				"""Environment :: Win32 (MS Windows)""",
			],
			'download_url': "https://sourceforge.net/project/showfiles.php?group_id=102251",
			'keywords': 'wxPython,AppBar,Start,TaskBar,OfficeBar,Win32,ctypes',
			'long_description' : """Win32 AppBar control for wxPython

wxAppBar provides a wrapper for the Win32 AppBar control
for use with wxPython.  AppBars (also called Task Bars)
are given a reserved area on one side of the screen so
that they are always visible.

The wxAppBar control is built using ctypes (no C/C++
code), so can be readily customised.
""",
			'platforms': ['Win32'],
		}
	else:
		extraArguments = {
		}

	### Now the actual set up call
	setup (
		name = "wxAppBar",
		version = "0.9.1a",
		description = "Win32 AppBar control for wxPython",
		author = "Mike C. Fletcher",
		author_email = "mcfletch@users.sourceforge.net",
		url = "http://wxappbar.sourceforge.net",
		license = "BSD-style, see license.txt for details",

		package_dir = {
			'wxappbar':'wxappbar',
		},

		packages = [
			'wxappbar', 
		],
		# non python files of examples      
		data_files = dataFiles,
		cmdclass = {'install_data':smart_install_data},
		**extraArguments
	)
	
