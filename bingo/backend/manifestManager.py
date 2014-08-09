import os
import subprocess
from bingo.backend.utils import *

# This class manages the manifest--it traverses the modules directory to find the
# names of all the modules. 

# Right now it's missing key functionality that we aren't able to do parameters
class ManifestManager(object):
	"""docstring for ManifestManager"""
	def __init__(self, backend):
		super(ManifestManager, self).__init__()
		self.backend = backend
		self.modulePath = os.path.dirname(os.path.realpath(__file__)) + "/modules"
		self.currentModules = []
		
	def initialize(self):

		# This initializes all the files and directories we need
		for directory in ["/etc/puppet", "/etc/puppet/manifests", "/etc/puppet/modules"]:
			try:
				command = "sudo ls " + directory
				msg = subprocess.check_output(command, shell=True)
			except Exception, e:
				command = "sudo mkdir " + directory
				runAndCatchException(command)
			return ""

		
		# This duplicates all the modules into the directories we created
		command = "sudo cp -r " + self.modulePath + "*" + " /etc/puppet/modules"
		runAndCatchException(command)
		runAndCatchException("sudo rm /etc/puppet/manifests/site.pp" )
		runAndCatchException("sudo touch /etc/puppet/manifests/site.pp" )

	# This checks to make sure that it's actually a puppet file we found			<------------------TODO
	# obviously it doesn't work right now 
	def verifyModule(self, pathname):
		return True

	# Returns semantic description of all the modules we found						<------------------TODO
	# TODO this should also understand when these can have options, and
	# present those options with a brief description
	def generateMenu(self):
		modules = [module for module in os.listdir(self.modulePath )]
		return modules

	# This appends the line in site.pp to include a certain module in the 
	# manifest
	def addModule(self, moduleName):
		if (self.verifyModule(moduleName)):
			if (moduleName not in self.currentModules):
				runAndCatchException("sudo sh -c \"echo 'include " + moduleName + "' >> /etc/puppet/manifests/site.pp\"")
				output("Added " + moduleName + " to the manifest\n")
				self.currentModules.append(moduleName)
			else:
				output("ERROR: You've already added that module!\n")
		else:
			output("ERROR: I don't know that module\n")