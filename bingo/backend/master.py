from bingo.backend import manifestManager
from bingo.backend import sshThread
from bingo.backend import configParser
from bingo.backend.utils import *

import subprocess
import re
import sys
import time
import os

# This is the class that models the backend of clusterBingo--it has two main parts:
# maintaining all the ssh connnections in a threadpool of sshThreads, and also 
# maintaining the manifest based off of the user input. 

# Heres how I handle SSL:
# 	I first clear out all SSL certificates from this machine. Then I have the 
# 	future agent clear out all of her certificates. Then I okay the handshake

# BIG TODO: It should also take in a configuration file and parse it before anything 						<------------------TODO
# else--that way we can bypass the command line interface--the command line should
# only be used in case anything was forgotten

class Backend(object):
	"""docstring for Backend"""
	def __init__(self, update=False, threaded=False):
		super(Backend, self).__init__()
		self.update = update
		self.threaded = threaded
		self.sshThreads = []
		# Getting all the information from our machine
		self.hostname = re.sub("\s+", "", subprocess.check_output('hostname')) 
		self.ipaddress = re.sub("\s+", "", subprocess.check_output(' facter ipaddress_eth1', shell=True))		# NOTE. THIS SHOULD BE EN0 if not on VM
		self.modulePath = os.path.dirname(os.path.realpath(__file__)) + "/../modules/"
		self.manifestManager = manifestManager.ManifestManager(self)
		self.configParser = configParser.ConfigParser(self)

	def setFrontend(self, frontend):
		self.frontend = frontend

	def getMachines(self):
		return [machine.ipaddress for machine in self.sshThreads]

	# This is the method that creates an SSHThread, based off of the parameters we pass in. 
	# NOTICE THAT THESE ARE REALLY POORLY HARD CODED. 														<------------------TODO
	def setMachine(self, ip="", username="vagrant", password="password", rsa="/vagrant/JASONHU.cer"):
		if (len(ip) < 1):
			return
		ip = re.sub("\s+", "", ip) 
		if not (isIPAddress(ip)):
			output("ERROR: " + ip + " isn't a valid IP\n")
			return
		thread = sshThread.sshThread(self, ip=ip, username=username, password=password, rsa=rsa)
		thread.initializeMachine()
		if thread.hostname in [t.hostname for t in self.sshThreads]:
			output("You already initialized that machine!\n")
			return

		# By default, I don't take advantage of threading because I want the REALLY 						<------------------TODO
		# pretty output. If you want to thread it, I recommend that you first disable the
		# output at this point. (Cehck the method output in utils.py)
		thread.start()
		if not (self.threaded):
			thread.join()

	# Helper method to get the machines that are pending certificates
	def getPendingCertificates(self):
		certs = []
		certificates = subprocess.check_output('sudo puppet cert list', shell=True).split("\n")
		for certificate in certificates:
			certificate = re.split("\s+", certificate)
			if (len(certificate) > 1):
				agentName = re.sub("\"", "", certificate[1])
				certs.append(agentName)
		return certs

	# When a sshthread tells the master to ask for a certification, it passes a reference of 
	# itself in, so that the master can add it to the pool
	def certify(self, thread):

		# Then sign the new certificate
		certificates = [certificate for certificate in self.getPendingCertificates() if len(certificate) > 0]
		attempts = 0
		while not (len(certificates) > 0):
			certificates = [certificate for certificate in self.getPendingCertificates() if len(certificate) > 0]
			time.sleep(1)
			attempts += 1
			if attempts > 10:
				break
			output("\tNo pending certificates. Attempting again ....\n")

		if thread.hostname in certificates:
			command = "sudo puppet cert sign " + thread.hostname
			subprocess.check_output(command, shell=True)
			output("\tJust verified " + thread.hostname + "\n")
			self.sshThreads.append(thread)
		else:
			output("\tWARNING: Certification timed out. Maybe " + thread.hostname + " already is verified?\n")

	def initializeSelf(self):
		# 0. Get the appropriate package manager
		packageManager = findPackageManager()
		if len(packageManager) > 0:
			self.packageManager = packageManager
			output("Using " + self.packageManager + " as the package manager\n")
		else:
			output("ERROR: Couldn't find a package manager. Exiting now\n")
			sys.exit(0)

		# 1. Ensure puppet and command is installed
		output("Installing programs ...\n")
		if self.update:
			output("\tRunning sudo " + self.packageManager + " update\n")
			subprocess.check_output("sudo " + self.packageManager + " -y update", shell=True)
		for program in ["puppet", "facter"]:
			ensureInstalled(program)
		output("Finished installation!\n")

		# 2. Make sure manifests are in place
		output("Populating /etc/puppet/modules ...\n")
		self.manifestManager.initialize()

		# 3. Clean up all certifiactes. Kill any existing master
		output("\tKilling all running puppets ... \n")
		processes = runAndCatchException("ps -e | grep puppet")
		processes = [re.split("\s+", line) for line in processes.split("\n")]
		for process in processes:
			if "puppet" in process:
				for i in range(len(process)):
					if (re.match("^\d+$", process[i])):
						runAndCatchException("sudo kill " + process[i])
						output("\t\tKilled " + process[i] + "\n")
		runAndCatchException("sudo rm -r /var/lib/puppet/ssl") 									# EW WARNING PATH HARDCODED <------------------------------

		# 4. Start the puppet master
		puppetPath = re.sub("\s+", "", subprocess.check_output("which puppet", shell=True))
		command = "sudo " + re.sub("\s+", "", puppetPath) + " master --mkusers"
		msg = subprocess.check_output(command, shell=True)

		# 5. Parse and execute the config file and command line arguments
		self.configParser.parseCommandLineArguments()	# this does nothing. 					<------------------TODO

	def generateMenu(self):
		return self.manifestManager.generateMenu()

	def getModules(self):
		return self.manifestManager.currentModules

	def addModule(self, moduleName):
		self.manifestManager.addModule(moduleName)

