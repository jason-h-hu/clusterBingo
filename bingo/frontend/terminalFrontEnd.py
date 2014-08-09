from bingo.frontend import frontendAbstract
from bingo.frontend import calligrapher
from bingo.backend import inputParser

import sys
from bingo.backend.utils import * 

# This is the class thast models the terminal interaction. It's
# a series of REPLs that walk the user through setting up the puppet
# master-agent configuration, and then presents the user with 
# a menu of possible options
class TerminalFrontEnd(frontendAbstract.Frontend):

	def __init__(self):
		super(TerminalFrontEnd, self).__init__()
		self.super = super(TerminalFrontEnd, self)
		self.inputParser = inputParser.InputParser(self)

	def quit(self):
		output("\n")
		output("Shutting down ... \n")
		output(calligrapher.banner("~"))
		self.super.quit()

	def introduction(self):
		output(calligrapher.banner("~"))
		output("CLUSTER BINGO 0.1\n")
		output("By Jason Hu\n")
		output(calligrapher.banner("~"))
		output("\n"*2)


	# This is where teh user feeds clusterBingo a list of ip addresses,
	# and then it'll spin up sshThreads for each one--each will go into 
	# the other machiens and install puppet adn then set up the master-agent
	# network

	# BIG TODO - Right now this only takes in ip addresses, but it'll be 		<------------------TODO
	# necessary to input the password, username, and RSA keys if necessary. 
	def ipREPL(self):
		output("1. SETTING UP MACHINES\n")
		output(calligrapher.banner("-"))
		output("\n")
		isMissingMachines = len(self.backend.sshThreads) < 1
		while isMissingMachines:
			output(calligrapher.prompt())
			inputText = sys.stdin.readline()
			if not self.inputParser.parseSTDIN(inputText):
				for ipaddress in re.split("\s+", inputText):
					if (isIPAddress(ipaddress)):
						self.backend.setMachine(ipaddress)
				if ((inputText) == "\n" and (len(self.backend.sshThreads) > 0)):
					break

	# This is where the user can choose from a list of possible 
	# pre-written manifests. The user then types in the list of
	# all the desired manifests it wants, and then the site.pp
	# file is automatically generated 

	# BIG TODO - Right now it can't do anything more then append				<------------------TODO
	# "include manifest.pp" in the site.pp file--it really should
	# be able to support a bit of parameters and so on. 
	def configREPL(self):
		output("\n2. CHECKING CONFIGURATIONS\n")
		output(calligrapher.banner("-"))
		output("\n")
		output("current manifest is:\n ")
		for module in self.backend.getModules():
			output ("\t" + module + " \n" )

		output("\n")

		output("the modules are:\n ")
		for module in self.backend.generateMenu():
			output ("\t" + module + " \n" )

		while True:
			output(calligrapher.prompt())
			inputText = re.sub("\n", "", sys.stdin.readline())
			if not self.inputParser.parseSTDIN(inputText):
				for arg in re.split("\s+", inputText):
					self.backend.addModule(arg)

	# This assembles the manifest.

	# BIG TODO - This right now just waits for the puppet 						<------------------TODO
	# agent to do its routine checks--it really should immediately 
	# kick the agent to udpate itslef--look into kick documentation
	# in puppet labs
	def runREPL(self):
		while True:
			output(calligrapher.prompt())
			inputText = sys.stdin.readline()
			if not self.inputParser.parseSTDIN(inputText):
				self.backend.addModule(inputText)

	# This 
	def mainREPL(self):
		self.ipREPL()			# prompts user to provide list of IP address/hostnames and RSA keys
		self.configREPL()

	# The topmost method call. Called by app.py
	def start(self):
		self.super.start()		# Put any necessary initializations here
		self.introduction()		# Prints the welcome script
		self.mainREPL()			# All the actual interface
		self.quit()