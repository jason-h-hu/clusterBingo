from bingo.backend import utils
from bingo.frontend import calligrapher
import subprocess

# This class is used to parse anythign the user inputs, comparing
# it against a list of known possible commands/options. If it matches
# those options, then it executes that command and returns True. Otherwise
# it returns false. This way we know, when we call this, whether we
# should continue parsing the input. 

class InputParser(object):

	def __init__(self, terminalFrontEnd):
		super(InputParser, self).__init__()
		self.terminal = terminalFrontEnd
		

	def parseSTDIN(self, string):

		if len(string) == 0:
			self.terminal.quit()

		splitString = utils.cleanupAndSplitTerminalInput(string)
		if len(splitString) > 0:
			cmd = splitString[0]

			if cmd == "quit" or cmd == "exit":
				self.terminal.quit()

			elif cmd == "help" or cmd == "-h" or cmd=="-h" or cmd == "--help":
				utils.output(calligrapher.showHelp())
				return True

			elif cmd == "clear":
				subprocess.call("clear")
				return True

			# TODO: This should also take in commands like 					<------------------TODO
			# ip which can let you add in more machines. 
			# include which lets you add modules to the manifest
			# and remove versions of both
		return False