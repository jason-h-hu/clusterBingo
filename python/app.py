#! /usr/bin/python
import json
import subprocess
import re
import sys
import argparse
import os.path

"""
To do:
0. Kinda comment
1. Add more parameters to check
2. Get SSH functionality up
3. pyMongo?
...
4. Bernie and Luke to clean up?
"""

# This organizes what we're looking for, the shell command to retrieve
# that information, and what specific fields within that printout we want.
# If fields is blank, this will return everything.
parameters = {	
				"filesystem": {
					"command": ["df", "-h", "/"], 
					"fields": []
				},
				"blockdev": {
					"command": ["sudo", "blockdev", "--report"], 
					"fields": []
				}
			}

verbose = False
destination = None
settings = {}

"""
A helper method for printing
"""
def output(jsonObject):
	if verbose:
		if isinstance(jsonObject, str):
			print jsonObject
		else:
			print json.dumps(jsonObject, indent=1)

def initialize():
	output("Checking python version ...")
	version = sys.version_info
	assert version.major >= 2
	assert version.minor >= 7

def parseArguments():
	parser = argparse.ArgumentParser(description="Checks that various system parameters are tuned properly")
	parser.add_argument("--parameters", "-p", help="A JSON file that describes the parameters we're interested in, and the terminal commands to run to get thems")
	parser.add_argument("--destination", "-d", help="Where we want to write the results to")
	parser.add_argument("--verbose", "-v", help="Whether we want it to be verbose", action="store_true")
	args = parser.parse_args()
	global verbose, destination, parameters
	verbose = args.verbose
	destination = args.destination
	parameters = args.parameters if args.parameters != None else parameters

"""
This assembles the dict holding all the parameters. 
"""
def getSettings():

	def parseSpaceSeparatedValues(terminalOutput):
		return [re.split("\s+", line) for line in terminalOutput.split("\n")]

	def packageParsedOutputAsDict(parsedOutput, fields=[]):
		if len(parsedOutput) > 1:
			results = []
			labels = parsedOutput[0]
			for i in range(1, len(parsedOutput)):
				row = parsedOutput[i]
				if len(row) > 1:
					result = {labels[j]:row[j] for j in range(len(row)) if (labels[j] in fields or len(fields) < 1)}
					results.append(result)
			return results if len(results) > 1 else results[0]

	global parameters
	if isinstance(parameters, str):
		parameters = json.load(open(parameters)) if os.path.isfile(parameters) else parameters

	for name in parameters:
		output("Getting " + name + " info ...")
		commands = parameters[name]
		try:
			# Find workaround for earlier python?
			results = subprocess.check_output(commands["command"])
			results = parseSpaceSeparatedValues(results)
			if len(results) > 1:
				settings[name] = packageParsedOutputAsDict(results, commands["fields"]) if "fields" in commands else packageParsedOutputAsDict(results)
		except subprocess.CalledProcessError as e:
			output("Couldn't read the " + name)


"""
This writes the output as a JSON to the desired destination
"""
def outputSettings():
	output(settings)
	global destination
	if destination is not None:
		fileEnding = destination.split(".")[-1]
		if fileEnding != "json" or fileEnding != "JSON":
			destination += ".json"
		with open(destination, 'w+') as outfile:
			outfile.write(json.dumps(settings, indent=1))

"""
The main line
"""
def main():
	parseArguments()
	initialize()
	getSettings()
	outputSettings()
	pass

if __name__ == '__main__':
	main()