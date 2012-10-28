"""Script to automatically generate wxAppBar documentation"""
import pydoc2

if __name__ == "__main__":
	excludes = [
		"Numeric",
		"_tkinter",
		"Tkinter",
		"math",
		"string",
		"twisted",
	]
	stops = [
	]

	modules = [
		'wxappbar',
		'__builtin__',
		'wxoo.windowdrag',
	]	
	pydoc2.PackageDocumentationGenerator(
		baseModules = modules,
		destinationDirectory = ".",
		exclusions = excludes,
		recursionStops = stops,
	).process ()
	