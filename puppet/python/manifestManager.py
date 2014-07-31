import os
import subprocess
from utils import *

class ManifestManager(object):
	"""docstring for ManifestManager"""
	def __init__(self, backend):
		super(ManifestManager, self).__init__()
		self.backend = backend
		self.modulePath = os.path.dirname(os.path.realpath(__file__)) + "/../modules"
		self.currentModules = []
		
	def initialize(self):
		for directory in ["/etc/puppet", "/etc/puppet/manifests", "/etc/puppet/modules"]:
			try:
				command = "sudo ls " + directory
				msg = subprocess.check_output(command, shell=True)
			except Exception, e:
				command = "sudo mkdir " + directory
				runAndCatchException(command)
			return ""

		
		command = "sudo cp -r " + self.modulePath + "*" + " /etc/puppet/modules"
		runAndCatchException(command)
		runAndCatchException("sudo rm /etc/puppet/manifests/site.pp" )
		runAndCatchException("sudo touch /etc/puppet/manifests/site.pp" )
		# self.addModule("mongodb")

	def verifyModule(self, pathname):
		return True

	def generateMenu(self):
		modules = [module for module in os.listdir(self.modulePath )]
		return modules

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