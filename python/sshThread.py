import json
import subprocess
import re
import sys
import argparse
import os.path
import threading
import socket
import outputParser
import surveyorCore
import surveyorGeneric
import paramiko
import settingsChecker

coreCommands = {}
genericCommands = {}

"""
This is called by each thread (one for each machine we want to check), to connect, call the appropriate shell commands, and then parse the output. 

This was written to accomodate a wide variety of possible outputs. The main helper method, parseTerminalOutput, has multiple helper functions--each one knows how to parse a certain type of output. parseTerminalOutput thus passes the raw printout through a series of regular expressions to determine the format, and then it calls the appropriate method. 
"""
def connectAndParseInput(configDict):

	# Try and connect first, to ensure a valid IP address
	ip = configDict["ip"]
	sshCommand = "ssh -t -i " + configDict["rsa"] if "rsa" in configDict else "ssh -t"
	sshCommand += " " + ip 
	try:
		subprocess.check_output((sshCommand + " ls"), stderr=open("app.log"), shell=True)
	except subprocess.CalledProcessError as e:
		output(str("Couldn't connect to " + ip + "\n"), 1)
		return

	# Initialize the return settings dict with the machine we're taking specs of
	global machineSettings
	machineSettings[ip] = {}

	# For every system setting we want to find
	for systemSetting in commands:
		output(str("Checking " + systemSetting + " ..."))
		commandInformation = commands[systemSetting]
		try:
			# Build the shell command
			shellCommand = sshCommand + " " + commandInformation["command"] 
			# Run the command
			terminalOutput = subprocess.check_output(shellCommand, stderr=open("app.log"), shell=True)
			terminalOutput = terminalOutput.replace("\r", "")

			# Parse the output according to specifications
			fields = commandInformation["fields"] if "fields" in commandInformation else []
			results = parseTerminalOutput(terminalOutput, fields)

			# Populate the results dict
			if results != None:
				machineSettings[ip][systemSetting] = results

		except subprocess.CalledProcessError as e:
			output(str("Couldn't read the " + systemSetting + "\n"), 1)

"""
This extends the thread class. A thread is created for every machine we're interested in
"""
class sshThread(threading.Thread):

	def __init__(self, configDict):
		super(sshThread, self).__init__()
		self.configDict = configDict
		self.sshConfig = self.configDict["ssh"]
		username = self.sshConfig["username"]
		self.ip = self.sshConfig["ip"]
		rsa = self.sshConfig["rsa"]
		
		# 1. Create ssh connection
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(str(self.ip), username=str(username), key_filename=str(rsa))

		self.ssh = ssh

		self.sc = surveyorCore.surveyorCore(self.ssh)
		self.sg = surveyorGeneric.surveyorGeneric(self.ssh)
		self.checker = settingsChecker.checker(self.configDict["desiredSettings"])
		self.output = {}
		self.conflicts = {}

	def constructSurveyors(self):
		self.surveyors = []
		if ("coreChecks" in self.configDict):
			coreChecks = self.configDict["coreChecks"]
			for check in coreChecks:
				if check == "blockdev":
					return self.blockdev()
				elif check == "cpu":
					return self.cpu()
				elif check == "filesystem":
					return self.filesystem()
				elif check == "kernel":
					return self.kernel()
				elif check == "largePages":
					return  self.largePages()
				elif check == "raid":
					return self.raid()
				elif check == "ssd":
					return self.ssd()
				elif check == "swapSpace":
					return self.swapSpace()

	def surveyAndCheck(self):
		username = self.sshConfig["username"]
		ip = self.sshConfig["ip"]
		rsa = self.sshConfig["rsa"]

		# 2. Run and parse every core value in the surveyorCore
		if ("coreChecks" in self.configDict):
			coreChecks = self.configDict["coreChecks"]
			for check in coreChecks:
				results = self.sc.survey(check)
				if results != None:
					self.output[check] = results
					checkedResults = self.checker.check(check, results)
					if checkedResults != None:
						self.conflicts[check] = checkedResults
		
		# 3. Run and parse every generic command in surveyorGeneric
		# if ("genericChecks" in self.configDict):
		# 	genericChecks = self.configDict["genericChecks"]
		# 	for name, check in genericChecks.items():
		# 		self.output[name] = self.sg.survey(check)
		# 		checkedResults = self.checker.check(name, results)
		# 		if checkedResults != None:
		# 			self.conflicts[name] = checkedResults
		
	def run(self):
		self.surveyAndCheck()
		self.ssh.close()

