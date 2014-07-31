import json
import subprocess
import re
import sys
import argparse
import os.path
import threading
import socket
from app import output

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
	results = {cleanup(line[0]): cleanup(line[1]) for line in parsedOutput if (len(line) > 1) and (line[0] in fields or len(fields) == 0)}
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
		labels = [cleanup(label) for label in parsedOutput[0]]
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
		return results

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
				results[cleanup(line[0])] = [cleanup(flag) for flag in re.split("[,\s+]", line[1]) if len(flag) > 0]
	if len(results) > 0:
		return results

"""
This just turns every line in the output into a string in a list
"""
def parseRegularOutput(terminalOutput, fields=[]):
	return [cleanup(line) for line in terminalOutput.split("\n")]


"""
This takes in the output from a terminal command, and then tries to format it to JSON. 
fields is optional--if designated, it will only populate the JSON with the specified fields. 
"""
def parseGenericOutput(terminalOutput, fields=[]):
		
	# Match the raw output against various regex's and try to determine which method to call
	results = None
	if re.search(".+:(\s+\d+)", terminalOutput, re.MULTILINE):
		output("Matches key value list\n")
		results = parseKeyValueList(terminalOutput, fields)

	elif re.search(".+:(\s+\S+)+", terminalOutput, re.MULTILINE):
		output("Matches colon list\n")
		results = parseColonListOutput(terminalOutput, fields)

	elif re.search("[{}\"\[\]]", terminalOutput, re.MULTILINE) or terminalOutput.count(" ")<1:
		output("Matches regular output\n")
		results = parseRegularOutput(terminalOutput, fields)

	elif re.search("[^:]+(\s+\S+)+", terminalOutput, re.MULTILINE) and terminalOutput.count("\n")>1:
		output("Matches table output\n")
		results = parseSpaceSeparatedTableOutput(terminalOutput, fields)

	else:
		output("Matches nothing. Using regular output\n")
		results = parseRegularOutput(terminalOutput, fields)
	return results