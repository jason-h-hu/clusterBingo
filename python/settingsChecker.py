import json
import subprocess
import re
import sys
import argparse
import os.path
import threading
import socket
import outputParser
import surveyorCore
import surveyorGeneric
import paramiko

class checker(object):

	def __init__(self, desiredSettingsDict):
		super(checker, self).__init__()
		self.desiredSettingsDict = desiredSettingsDict

	"""
	This is a recursive helper method that looks over a scalar value or a list of scalar values, and tries to match them against the desired setting. The desired setting might be expressed as a dictionary, a value, a list of dictionaries, or a list of values. 

	This takes advantage of the other helper method, dictCompare, which tries to find a key value pair within a dict or in a list of dicts
	"""
	def valueCompare(self, element, setting):

		# Case 1: setting is a dict. Use dictCompare over every key/value pair
		if isinstance(setting, dict):
			for field2, setting2 in setting.items():
				result = self.dictCompare(element, field2, setting2)
				if result != None:
					return result

		# Case 2: setting is a list. Recursively call this over every element in the list.
		elif isinstance(setting, list):
			for setting2 in setting:
				result = self.valueCompare(element, setting2)
				if result != None:
					return result

		# Case 3: the setting is a string or int. Element is a list.	
		elif isinstance(element, list):
			for element2 in element:
				result = self.valueCompare(element2, setting)
				if result != None:
					return result

		# Case 3: the setting is a string or int. Element is a dict.	
		elif isinstance(element, dict):
			for field2, setting2 in element.items():
				result = self.valueCompare(setting2, setting)
				if result != None: 
					return result

		# Case 4: They're not a data structure
		else:

			# Case 4a: They're strings, in which case we can take advantage of regex's
			if (isinstance(setting, str) or isinstance(setting, unicode)) and (isinstance(element, str) or isinstance(element, unicode)):
				if re.search( str(setting), str(element) ):
					return element

			# Case 4b: Just compare them
			elif element == setting:
				return element

		# None of the comparisons returned true. Return false
		return None

	"""
	This compares a list, dictionary, or scalar against a key/value pair (written as field/setting).

	This takes advantage of the helper method, valueCompare, which tries to match a list, dictionary, or scalar against a single value, or list of values
	"""
	def dictCompare(self, struct, field, setting):

		# Case 1: We're trying to find a key/value pair in a dictionary. Iterate over all the key/value pairs and make the comparison
		if isinstance(struct, dict):
			for key, value in struct.items():
				# Case 1a: Keys match. Try to match the values.
				if key == field:
					result = self.valueCompare(value, setting)
					if result != None:
						return result
				# Case 1b: Keys don't match. Recursively go down the data structure. 
				else:
					result = self.dictCompare(value, field, setting)
					if result != None:
						return result

		# Case 2: If we're trying to find a key/vallue pair in a list, we iterate over the values and recursivly call dictCompares
		elif isinstance(struct, list):
			for value in struct:
				result = self.dictCompare(value, field, setting)
				if result != None:
					return result

		# All our comparisons failed. Return false.
		return None

	def check(self, check, results):
		returnVal = {	"found": False,
						"expected": "",
						"observed": ""
					}
		if check in self.desiredSettingsDict:
			returnVal["expected"] = self.desiredSettingsDict[check]
			found = self.valueCompare(results, self.desiredSettingsDict[check])
			returnVal["found"] = found != None
			returnVal["observed"] = found if found != None else results
			return returnVal
		return None