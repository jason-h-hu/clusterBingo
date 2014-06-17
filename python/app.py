#! /usr/bin/python
import json
import subprocess
import re
import sys
import argparse
import os.path
import threading
import socket

"""
To do:
1. Cleanup output
2. More robust regex
3. 
?. Bernie and Luke to clean up?
"""

config = None		# This is going to hold the JSON file that describes all the configurations we need. 
verbose = False		# A flag for whether we want to print out
destination = None	# This is going to hold the path to the output file we desired. If not specified by the user it'll just print instead
machineSettings = {}		# This dict is going to be populated with all the settings we find and parse. We'll then check it against a list of desired settings and values

"""
A helper method for printing
"""
def output(text, err=0):
	if verbose or err>0:
		if isinstance(text, str):
			sys.stdout.write( text )
		elif isinstance(text, dict):
			sys.stdout.write( json.dumps(text, indent=1) )

"""
This was written to ensure that we have the proper version of python.

Other similar checks should go here. 

Note: This is called before we parse the command line arguments
"""
def initialize():
	output("Checking python version ...\n")
	version = sys.version_info
	assert version.major >= 2
	assert version.minor >= 7

"""
This checks all the command line arguments passed in, and sets all the global variables accordingly.
"""
def parseArguments():

	# Define all the possible command line arguments
	parser = argparse.ArgumentParser(description="Checks that various system config are tuned properly")
	parser.add_argument("--config", "-c", help="A JSON file that describes the config we're interested in, and the terminal commands to run to get thems")
	parser.add_argument("--destination", "-d", help="Where we want to write the results to")
	parser.add_argument("--verbose", "-v", help="Whether we want it to be verbose", action="store_true")
	args = parser.parse_args()

	# And then read them, and set the global variables
	global verbose, destination, config
	verbose = args.verbose
	destination = args.destination
	config = args.config if args.config != None else config
	if isinstance(config, str):
		config = json.load(open(config)) if os.path.isfile(config) else config


"""
This takes in the output from a terminal command, and then tries to format it to JSON. 
fields is optional--if designated, it will only populate the JSON with the specified fields. 
"""
def parseTerminalOutput(terminalOutput, fields=[]):

	"""
	This helps remove trailing whitespace, and anything else
	"""
	def cleanup(text):
		text = re.sub("^\s+|\s+$|[\"<>\[\]()]", "", text)
		text = re.sub("\s+", " ", text)
		return text

	"""
	terminalOutput is the string output by the terminal. This turns an output of the form:
		key1: value1
		key2: value2
		...
	into a dict of the form:
		{	key1: value1,
			key2: value2,
			...
		}
	"""
	def parseKeyValueList(terminalOutput, fields=[]):
		parsedOutput = [line.split(":") for line in terminalOutput.split("\n")]
		results = {line[0]: cleanup(line[1]) for line in parsedOutput if (len(line) > 1) and (line[0] in fields or len(fields) == 0)}
		return results

	"""
	terminalOutput is the string output by the terminal. This turns an output of the form:
			category1     category2      category3 ...
			value1        value2         value3
			value4        value5         value6
	into a dict of the form:
		[
			{	category1: value1,
				category2: value2,
				category3: value3
			},
			{	category1: value4,
				category2: value5,
				category3: value6
			}
		]
	"""
	def parseSpaceSeparatedTableOutput(terminalOutput, fields=[]):
		parsedOutput = [re.split("\s+", line) for line in terminalOutput.split("\n")]
		if len(parsedOutput) > 1:
			results = []
			labels = parsedOutput[0]
			for i in range(1, len(parsedOutput)):
				row = parsedOutput[i]
				if len(row) > 1:
					result = {}
					for j in range(len(row)):
						if j < len(labels):
							if (labels[j] in fields or len(fields) < 1):
								result[labels[j]] = cleanup(row[j])
					# result = {labels[j]:row[j] for j in range(len(row)) if (labels[j] in fields or len(fields) < 1) and len(labels[j])> 0}
					results.append(result)
			return results if len(results) > 1 else results[0]

	"""
	terminalOutput is the string output by the terminal. This turns an output of the form:
			category1 : value1, value2, value3, ...
			category2 : value4, value5, value6, ...
	into a dict of the form:
		{
			category1: [value1, value2, value3 ...],
			category2: [value4, value5, value6 ...]
		}
	"""
	def parseColonListOutput(terminalOutput, fields=[]):
		parsedOutput = [line.split(":") for line in terminalOutput.split("\n")]
		results = {}
		for line in parsedOutput:
			if len(line) == 2:		
				if line[0] in fields or  len(fields) == 0:
					results[line[0]] = [cleanup(flag) for flag in re.split("[,\s+]", line[1]) if len(flag) > 0]
		if len(results) > 0:
			return results

	"""
	This just turns every line in the output into a string in a list
	"""
	def parseRegularOutput(terminalOutput, fields=[]):
		return [cleanup(line) for line in terminalOutput.split("\n")]
		
	# Match the raw output against various regex's and try to determine which method to call
	results = None
	if re.search(".+:(\s+\d+)", terminalOutput, re.MULTILINE):
		output("Matches key value list\n")
		results = parseKeyValueList(terminalOutput, fields)
	elif re.search(".+:(\s+\S+)+", terminalOutput, re.MULTILINE):
		output("Matches colon list\n")
		results = parseColonListOutput(terminalOutput, fields)
	elif re.search("[{}\"\[\]]", terminalOutput, re.MULTILINE):
		output("Matches regular output\n")
		results = parseRegularOutput(terminalOutput, fields)
	elif re.search("[^:]+(\s+\S+)+", terminalOutput, re.MULTILINE):
		output("Matches table output\n")
		results = parseSpaceSeparatedTableOutput(terminalOutput, fields)
	else:
		output("Matches nothing. Can't understand output\n")
	return results

"""
This is called by each thread (one for each machine we want to check), to connect, call the appropriate shell commands, and then parse the output. 

This was written to accomodate a wide variety of possible outputs. The main helper method, parseTerminalOutput, has multiple helper functions--each one knows how to parse a certain type of output. parseTerminalOutput thus passes the raw printout through a series of regular expressions to determine the format, and then it calls the appropriate method. 
"""
def connectAndParseInput(sshDict):

	# Try and connect first, to ensure a valid IP address
	ip = sshDict["ip"]
	try:
		if ip.find("@") > 0:
			host = ip[ip.find("@")+1:]
			socket.gethostbyname(host)
		else: 
			return
	except socket.error:
		output(str("Error: Couldn't find the ip address " + ip + "\n"), 1)
		return

	# Initialize the return settings dict with the machine we're taking specs of
	global machineSettings
	machineSettings[ip] = {}
	
	# For every system setting we want to find
	for systemSetting in config["commands"]:
		output(str("Getting " + systemSetting + " info ... "))
		commandInformation = config["commands"][systemSetting]
		try:
			# Build the shell command
			shellCommand = "ssh -t -i " + sshDict["rsa"] if "rsa" in sshDict else "ssh -t -i"
			shellCommand += " " + ip + " " + commandInformation["command"] 

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
			output(str("Couldn't read the " + name + "\n"), 1)


"""
This extends the thread class. A thread is created for every machine we're interested in
"""
class sshThread(threading.Thread):

	def __init__(self, sshDict):
		super(sshThread, self).__init__()
		self.sshDict = sshDict

	def run(self):
		connectAndParseInput(self.sshDict)
		

"""
This assembles the dict holding all the config. 
"""
def getSettings():

	threads = [sshThread(ssh) for ssh in config["ssh"]]

	for thread in threads:
		thread.start()

	for thread in threads:
		thread.join()

"""
This compares the populated machineSettings dict, which is populated with all the settings of the various machines we're interested in, and it compares it against a desiredSettings dict, which has key-value pairs for the settings and values we want, respectively. 

Because we don't know the structure of the machineSettings dict ahead of time, the way we verify this is by traversing down the data structure, checking the various key-value pairs as we go. This is accomplished by two recursive methods: valueCompare and dictCompare, for when we want to find an element within a list and for when we want to match two dictionary entries, respectively. The two will call each other, based off of the type of the elements of key/values stored within. 

The desiredSettings JSON object--specified in the config file--supports nesting. 
"""
def compareSettings():

	"""
	This is a recursive helper method that looks over a scalar value or a list of scalar values, and tries to match them against the desired setting. The desired setting might be expressed as a dictionary, a value, a list of dictionaries, or a list of values. 

	This takes advantage of the other helper method, dictCompare, which tries to find a key value pair within a dict or in a list of dicts
	"""
	def valueCompare(element, setting):

		# Case 0: element is actually a list of values
		if isinstance(element, list):
			for element2 in element:
				if valueCompare(element2, setting):
					return True

		# Case 1: setting is a dict. Use dictCompare over every key/value pair
		if isinstance(setting, dict):
			for field2, setting2 in setting.items():
				if dictCompare(element, field2, setting2):
					return True

		# Case 2: setting is a list. Recursively call this over every element in the list.
		elif isinstance(setting, list):
			for setting2 in setting:
				if valueCompare(element, setting2):
					return True
	
		# Case 3: They're not a data structure
		else:

			# Case 3a: They're strings, in which case we can take advantage of regex's
			if isinstance(setting, str) and isinstance(element, str):
				return re.search(element, setting);

			# Case 3b: Just compare them
			else:
				return element == setting

		# None of the comparisons returned true. Return false
		return False

	"""
	This compares a list, dictionary, or scalar against a key/value pair (written as field/setting).

	This takes advantage of the helper method, valueCompare, which tries to match a list, dictionary, or scalar against a single value, or list of values
	"""
	def dictCompare(struct, field, setting):

		# Case 1: We're trying to find a key/value pair in a dictionary. Iterate over all the key/value pairs and make the comparison
		if isinstance(struct, dict):
			for key, value in struct.items():
				# Case 1a: Keys match. Try to match the values.
				if key == field:
					if valueCompare(value, setting):
						return True
				# Case 1b: Keys don't match. Recursively go down the data structure. 
				else:
					if dictCompare(value, field, setting):
						return True

		# Case 2: If we're trying to find a key/vallue pair in a list, we iterate over the values and recursivly call dictCompares
		elif isinstance(struct, list):
			for value in struct:
				if dictCompare(value, field, setting):
					return True

		# All our comparisons failed. Return false.
		return False

	for field, setting in config["desiredSettings"].items():
		for ip in machineSettings:
			if not dictCompare(machineSettings[ip], field, setting):
				print ip, " fails ", field

"""
This writes the output as a JSON to the desired destination
"""
def outputSettings():
	global destination
	global machineSettings
	if destination is not None:
		fileEnding = destination.split(".")[-1]
		if fileEnding != "json" and fileEnding != "JSON":
			destination += ".json"
		with open(destination, 'w+') as outfile:
			outfile.write(json.dumps(machineSettings, indent=1))

"""
The main line
"""
def main():
	parseArguments()
	initialize()
	getSettings()
	compareSettings()
	outputSettings()
	
if __name__ == '__main__':
	main()