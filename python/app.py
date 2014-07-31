#! /usr/bin/python
"""
CLUSTER BINGO
version 0.0

ClusterBingo's goal is to ensure that multiple machines are running similar configurations, in regard to java version, read ahead size, filesystem, etc. Most of these parameters can be done by hand via various shell commands, but this would entail connecting to all the various machines to check, which would be tedious and error prone. 

Instead, this inital verion of ClusterBingo provides a way to organize the various machines and commands, as a way to automate the process. This should take a configuration JSON file, which specifies a list of IP addresses and the path to the RSA key, as well as a list of parameters and shell commands used to query for those parameters. 

ClusterBingo 0.0 connects to the various machines via ssh and calls the desired commands. It tries to be smart about parsing the output into JSON format, by comparing it against a list of known regexs describing possible outputs and then calling an appropriate parsing method. 

After assembling all the parameters over all the machines, it then can optionally compare it against a list of desired outcomes. It'll report back which ones are missing. 

To do:
...
?. Use MongoS instance to generate IP addresses

"""
import json
import subprocess
import re
import sys
import argparse
import os.path
import threading
import socket
import sshThread
import calligrapher
import paramiko
import time
from myUtil import *

configDict = {
	"ssh": [],
	"coreChecks": [],
	"desiredSettings": {}
} 

coreChecks = ["blockdev", "cpu", "filesystem", "kernel", "largePages", "raid", "ssd", "swapSpace"]

verbose = True		# A flag for whether we want to print out
threaded = False
destination = None			# This is going to hold the path to the output file we desired. If not specified by the user it'll just print instead
machineSettings = {}		# This dict is going to be populated with all the settings we find and parse. We'll then check it against a list of desired settings and values
conflicts = {}


def quit():
	output("\n")
	output("Shutting down ... \n")
	output(calligrapher.banner("~"))
	sys.exit(0)

def initialize():
	version = sys.version_info
	assert version.major >= 2
	if version.major == 2:
		assert version.minor >= 7
	subprocess.call("clear")

def addIPInput(terminalInput):
	ipPath = findJSONFile(terminalInput)
	if ipPath != None:
		parseConfig(ipPath)
	else:
		parsedInput = terminalInput.replace("\n", "")
		parsedInput = re.split(",\s+", parsedInput)
		parsedInput = [[arg for arg in re.split("\s+", ip) if len(arg) > 0] for ip in parsedInput if len(ip) > 0]
		for triplet in parsedInput:
			if isValidIPInput(triplet):
				username = triplet[0]
				ip=triplet[1]
				rsa=triplet[2]
				addIP(username, ip, rsa)
				
def addIP(username=None, ip=None, rsa=None):
	parsedIP = {"username": username, "ip": ip}
	if rsa != None:
		parsedIP["rsa"] = rsa
	configDict["ssh"].append(parsedIP)	

def addCheck(terminalInput, checks=[]):
	terminalInput = cleanupAndSplitTerminalInput(terminalInput)
	checks.extend(terminalInput)
	known = []
	unknown = []
	for check in checks:
		check = str(check)
		if isinstance(check, str):
			if check in coreChecks:
				if check not in configDict["coreChecks"]:
					configDict["coreChecks"].append(check)
			else:
				unknown.append(str(check))
	if len(unknown) > 0:
		output("ERROR: I don't understand " + "".join(unknown) + "\n")

def addDesiredSetting(setting, value):
	if setting in coreChecks:
		configDict["desiredSettings"][setting] = value
	else:
		output("ERROR: I don't understand " + str(setting) + "\n")

def addOutput(output):
	global destination
	if output != None:
		if isinstance(output, str) or isinstance(output, unicode):
			output = cleanupWhiteSpace(output)
			destination = generateJSONName(output)

def parseConfig(config):
	config = findJSONFile(config)
	if  config != None:
		config = json.load(open(config)) 
		if "ssh" in config:
			if isinstance(config["ssh"], list):
				for ip in config["ssh"]:
					if isinstance(ip, dict):
						if "username" in ip and "ip" in ip:
							if "rsa" in ip:
								addIP(username=ip["username"], ip=ip["ip"], rsa=ip["rsa"])
							else:
								addIP(username=ip["username"], ip=ip["ip"])

		if "coreChecks" in config:
			if isinstance(config["coreChecks"], list):
				for check in config["coreChecks"]:
					addCheck(check)
			# configDict["coreChecks"] = config["coreChecks"]
		if "desiredSettings" in config:
			if isinstance(config["desiredSettings"], dict):
				for check, value in config["desiredSettings"].items():
					addDesiredSetting(check, value)
			# configDict["desiredSettings"] = config["desiredSettings"]
		if "output" in config:
			if isinstance(config["output"], str) or isinstance(config["output"], unicode):
				addOutput(config["output"])
				# destination = config["output"]

def parseSTDIN(string):

	if len(string) == 0:
		quit()

	splitString = cleanupAndSplitTerminalInput(string)
	if len(splitString) > 0:
		cmd = splitString[0]

		if cmd == "quit" or cmd == "exit":
			quit()

		elif cmd == "help" or cmd == "-h" or cmd=="-h" or cmd == "--help":
			output(calligrapher.showHelp())
			return True

		# Print current configuration
		elif cmd == "setting" or cmd == "settings" or cmd == "-s" or cmd == "--s":
			settingDisplay = calligrapher.configuration( ips = configDict["ssh"], output=destination, settings=configDict["desiredSettings"], checks=configDict["coreChecks"])
			output(str(settingDisplay))
			return True

		elif cmd == "clear":
			subprocess.call("clear")
			return True

		elif cmd == "-i" or cmd == "ip" or cmd == "-ip" or cmd == "--ip":
			addIPInput("".split(splitString[1:]))
			output(calligrapher.outputIP(configDict["ssh"]))
			return True

		elif cmd == "-c" or cmd == "configuration" or cmd == "-configuration" or cmd == "--configuration":
			parseConfig("".join(splitString[1:]))
			settingDisplay = calligrapher.configuration( ips = configDict["ssh"], output=destination, settings=configDict["desiredSettings"], checks=configDict["coreChecks"])
			output(str(settingDisplay))
			return True

		elif cmd == "-ch" or cmd == "check" or cmd == "-check" or cmd == "--check":
			addCheck("".join(splitString[1:]))
			output(calligrapher.outputChecks(configDict["coreChecks"]))
			return True

		elif cmd == "-d" or cmd == "destination" or cmd == "-destination" or cmd == "--destination":
			addOutput("".join(splitString[1:]))
			output(calligrapher.outputDestination(destination))
			return True

	return False

"""
This checks all the command line arguments passed in, and sets all the global variables accordingly.
"""
def parseArguments():

	# Define all the possible command line arguments
	parser = argparse.ArgumentParser(description="Checks that various system configurations are tuned properly")
	parser.add_argument("--config",			"-c", 	help="A JSON file that describes the machines we want to use, the list of core checks we want to run, and a list of optional custom checks. It also can have a field for the desired settings we want to see.")
	parser.add_argument("--ip", 			"-i", 	help="A JSON file that describes the usernames, ip addresses, and rsa keys of all the machines we want to survey")
	parser.add_argument("--core", 			"-cc", 	help="A list of the core checks we want to survey")
	parser.add_argument("--generic", 		"-gc", 	help="A list of the custom checks we want to survey, stored as a JSON of key:value where the key and value are the name and shell command respectively")
	parser.add_argument("--settings", 		"-ds", 	help="A dictionary of desired settings, where the key: value is the field name: desired value respectively.")
	parser.add_argument("--destination", 	"-d", 	help="Where we want to write the results to")
	parser.add_argument("--verbose", 		"-v", 	help="Whether we want it to be verbose", action="store_true")
	parser.add_argument("--threading", 		"-t", 	help="Whether we want it to be threaded", action="store_true")
	args = parser.parse_args()

	# And then read them, and set the global variables
	global configDict, destination, verbose, threaded
	# verbose = args.verbose
	threaded = args.threading

	parseConfig(args.config)
	addOutput(args.destination)

	def checkAndOpen(filepath):
		assert isinstance(filepath, str) or isinstance(filepath, unicode)
		assert os.path.isfile(filepath)
		return json.load(open(filepath)) 

	if args.ip != None:
		configDict["ipDict"] = checkAndOpen(args.ip)

	if args.core != None:
		configDict["coreChecks"] = checkAndOpen(args.core)

	if args.settings != None:
		configDict["desiredSettings"] = checkAndOpen(args.settings)

def introduction():
	# Print the introduction
	output(calligrapher.banner("~"))
	output("CLUSTER BINGO 0.0\n")
	output("By Jason Hu\n")
	output(calligrapher.banner("~"))
	output("\n"*2)

def ipREPL():
	# Check that we have a valid IP address, or IP address JSON file
	output("1. ESTABLISHING IP ADDRESSES\n")
	output(calligrapher.banner("-"))
	output("\n")
	
	validIPs = len(configDict["ssh"])>0

	while not validIPs:
		validIPprompt = "Please specify a list of machines you want to survey via their IP address, the username you'd like to SSH as, and the path to the RSA key, if necessary."
		validIPprompt = calligrapher.columnify(validIPprompt, 1)
		output(validIPprompt+"\n"*2)
		output("\te.g.\tusername 127.32.10.101 /Users/login/Keys/KEY.pem,\n")
		output("\t\tconfig.json"+"\n"*2)
		output(calligrapher.prompt())
		instring = sys.stdin.readline()
		if not parseSTDIN(instring):
			addIPInput(instring)

		validIPs = len(configDict["ssh"])>0
	output(calligrapher.outputIP(configDict["ssh"]))

def configREPL():
	output("\n")
	output("2. CHECKING CONFIGURATIONS\n")
	output(calligrapher.banner("-"))
	output("\n")

	validChecks = len(configDict["coreChecks"]) > 0
	while not validChecks:
		output(calligrapher.promptChecks())
		output(calligrapher.outputChecks(configDict["coreChecks"]))

		# Ask for checks if we don't have any
		output(calligrapher.prompt())
		instring = sys.stdin.readline()
		if not parseSTDIN(instring):

			# If it's just [ENTER] we use everything
			if instring == "\n":
				configDict["coreChecks"] = list(coreChecks)
				output("Using all the checks\n\n")
			# Otherwise we parse the list, and print out warnings for things we don't understand
			else:
				instring = instring.replace("\n", "")
				parsedChecks = re.split(",*\s*", instring)
				for check in parsedChecks:
					if check in coreChecks:
						configDict["coreChecks"].append(check)
					else:
						output("ERROR: Couldn't understand " + check + "\n")

		validChecks = len(configDict["coreChecks"]) > 0
	output(calligrapher.outputChecks(configDict["coreChecks"]))

"""
This assembles the dict holding all the config. 
"""
def getSettings():

	output("\tGetting settings ...\n")
	threads = []
	for ssh in configDict["ssh"]:
		threads.append({
			"ssh": ssh, 
			"coreChecks": configDict["coreChecks"], 
			"desiredSettings": configDict["desiredSettings"]
		})

	threads = [sshThread.sshThread(thread) for thread in threads]
	
	for thread in threads:
		thread.start()
		if not threaded:
			thread.join()

	if threaded:
		for thread in threads:
			thread.join()
	for thread in threads:
		machineSettings[thread.ip] = thread.output
		conflicts[thread.ip] = thread.conflicts

"""
This writes the output as a JSON to the desired destination
"""
def outputSettings():
	output("\tOutputting settings ...\n")
	dst = destination
	with open(dst, 'w+') as outfile:
		outfile.write(json.dumps(machineSettings, indent=1))
	output("\tOutput results to " + dst +"\n")

def runREPL():
	output("\n")
	output("3. RUNNING\n")
	output(calligrapher.banner("-"))
	while True:
		output("Type 'settings' to check configuration before running. Hit [ENTER] to run\n\n")

		# Ask for checks if we don't have any
		output(calligrapher.prompt())
		instring = sys.stdin.readline()
		if not parseSTDIN(instring):
			if instring == "\n":
				break;
			else:
				output("ERROR: I don't understand " + instring)
	getSettings()
	
def outputREPL():
	output("\n")
	output("4. OUTPUT\n")
	output(calligrapher.banner("-"))
	output(re.sub(r"[{}][\n,]*", "", json.dumps(machineSettings, indent=1)))
	output("\n")
		
	# output(calligrapher.settingsOutput(machineSettings))

	if len(configDict["desiredSettings"]) > 0:
		output(calligrapher.conflictsOutput(conflicts))


	output("The current output is " + str(destination) + "\n")
	output("To set a destination, type: \n")
	output("\t-d [filename]\n")
	output("\tdestination [filename]\n")
	output("\n")
	while True:
		output("Set a destination, if desired. Otherwise, hit [ENTER] to quit\n\n")

		# Ask for checks if we don't have any
		output(calligrapher.prompt())
		instring = sys.stdin.readline()
		if not parseSTDIN(instring):
			if instring == "\n":
				break;
			else:
				output("ERROR: I don't understand " + instring)

	if destination != None:
		outputSettings()

def mainREPL():

	# main loop
	ipREPL()
	configREPL()
	runREPL()
	outputREPL()

"""
The main line
"""
def main():
	initialize()
	parseArguments()
	introduction()
	mainREPL()
	quit()
	# getSettings()
	# outputSettings()
	
if __name__ == '__main__':
	main()