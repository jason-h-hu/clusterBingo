import subprocess
import sys
import re

def output(text, err=0):
	sys.stdout.write( text )

def cleanupAndSplitTerminalInput(terminalInput):
	terminalInput = terminalInput.replace("\n", "")
	terminalInput = re.split(",*\s+", terminalInput)
	return terminalInput

def isIPAddress(string):
	return (re.match("\d+\.\d+\.\d+\.\d+", string))

def runAndCatchException(command):
	try:
		msg = subprocess.check_output(command, shell=True)
		return msg
	except Exception, e:
		command = re.sub("\n", "", command)
		output("Tried running " + command + " but failed\n")
	return ""

def findPackageManager():
	packageManagers = ["apt-get", "yum", "rpm"]
	for packageManager in packageManagers:
		path = re.sub("\s+", "", subprocess.check_output("which " + packageManager, shell=True))
		if (len(path) > 1):
			return path
	return ""

# program is the name of the program, aka the package name
# command is the name of the command run from the terminal
def ensureInstalled(program, command=""):
	output("\tLooking for " + program + " ... ")
	if len(command) == 0:
		command = program
	path = subprocess.check_output("which " + command, shell=True)

	# 2. If the program is currently not installed
	if (len(path) < 1):
		output(" can't find it. \n")
		output("\tStarting to install ... ")

		# 2.a Call the appropriate package manager
		packageManager = findPackageManager()
		command = "sudo " + packageManager + " -y install " + program
		msg = subprocess.check_output(command, shell=True)
		output("installed " + program + "!\n")

	else:
		output("found it!\n")
