import frontend
import calligrapher
import inputParser

import sys
from utils import * 

class TerminalFrontEnd(frontend.Frontend):

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


	def ipREPL(self):
		output("1. SETTING UP MACHINES\n")
		output(calligrapher.banner("-"))
		output("\n")
		# output("BYPASSING IP INSERTION FOR TESTING! see TerminalFrontEnd.py line 33\n\n\n")
		# return
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
		# output("\n")
		while True:
			output(calligrapher.prompt())
			inputText = re.sub("\n", "", sys.stdin.readline())
			if not self.inputParser.parseSTDIN(inputText):
				for arg in re.split("\s+", inputText):
					self.backend.addModule(arg)

	def runREPL(self):
		while True:
			output(calligrapher.prompt())
			inputText = sys.stdin.readline()
			if not self.inputParser.parseSTDIN(inputText):
				self.backend.addModule(inputText)
				pass

	def mainREPL(self):
		self.ipREPL()			# prompts user to provide list of IP address/hostnames and RSA keys
		self.configREPL()
		# self.runREPL()

	def start(self):
		self.super.start()		# will parse arguments here
		self.introduction()
		self.mainREPL()
		self.quit()