import subprocess
import sys
import re
import os 

# This is where we put all the random functions we wrote
# that might do useful functions for everyone

def output(text, err=0):
	sys.stdout.write( text )

def cleanupAndSplitTerminalInput(terminalInput):
	terminalInput = terminalInput.replace("\n", "")
	terminalInput = re.split(",*\s+", terminalInput)
	return terminalInput

def isIPAddress(string):
	return (re.match("\d+\.\d+\.\d+\.\d+", string))

# Runs a command and catches all exceptions indiscriminantly
def runAndCatchException(command):
	try:
		msg = subprocess.check_output(command, shell=True)
		return msg
	except Exception, e:
		command = re.sub("\n", "", command)
		output("Tried running " + command + " but failed\n")
	return ""

# This is a really unsophisticated way of finding our package
# mangager--it simply iterates over a list of pacakge managers
# until one returns postiviely on "which"
def findPackageManager():
	packageManagers = ["apt-get", "yum", "rpm", "brew"]
	for packageManager in packageManagers:
		try:
			path = re.sub("\s+", "", subprocess.check_output("which " + packageManager, shell=True))
			if (len(path) > 1):
				return path
		except Exception, e:
			pass
	return ""

# This ensures that a program is isntalled on this computer. 
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

# This ensures a file exists--if a .json suffix doesnt
# exist it'll append it.
def ensureValidJSONFile(path):
	if isinstance(path, str) or isinstance(path, unicode):
		path = str(path.replace("\n", ""))
		path = path.replace(" ","")
	if not (re.search(".*\.json", path) or re.search(".*\.JSON", path)):
		path += ".json"	
	if os.path.exists(path):
		if os.path.isfile(path):
			return path 
	return None