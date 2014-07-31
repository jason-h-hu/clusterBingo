import utils
import calligrapher
import subprocess

class InputParser(object):
	"""docstring for InputParser"""
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

		return False