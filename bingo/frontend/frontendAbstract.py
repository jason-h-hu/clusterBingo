import sys

# This is the abstract interface for the front end, 
# in case we ever want to make another interface or
# a graphical interface.
class Frontend(object):
	"""docstring for Frontend"""
	def __init__(self):
		super(Frontend, self).__init__()
		
	def setBackend(self, backend):
		self.backend = backend

	def parseArguments(self):
		pass

	def start(self):
		self.parseArguments()

	def quit(self):
		sys.exit(0)