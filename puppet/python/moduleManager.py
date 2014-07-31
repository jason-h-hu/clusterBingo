class moduleManagerFactory(object):
	"""docstring for moduleManagerFactory"""
	def __init__(self, arg):
		super(moduleManagerFactory, self).__init__()
		self.arg = arg

	def generateModuleManager(self, moduleName):
		pass

class moduleManager(object):
	"""docstring for moduleManager"""
	def __init__(self, arg):
		super(moduleManager, self).__init__()
		self.arg = arg
	
	# This returns two strings: Its own name, and a 
	# description of what it does and its parameters
	def getDescription(self):
		pass

	# This 
	def getManifestDeclaration(self):
		pass

	def setParameter(self, parameters):
		pass