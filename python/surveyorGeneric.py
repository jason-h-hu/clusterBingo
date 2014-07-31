import json
import subprocess
import re
import sys
import argparse
import os.path
import threading
import socket
import outputParser

class surveyorGeneric(object):

	def __init__(self, ssh):
		super(surveyorGeneric, self).__init__()
		self.ssh = ssh
		
	def survey(self, command):
		shellCommand = command["command"] if isinstance(command, dict) else command
		fields = command["fields"] if isinstance(command, dict) else []
		stdin, stdout, stderr = self.ssh.exec_command(shellCommand)
		output = ""
		for line in stdout.readlines():
			output += line
		if len(output) == 0:
			for line in stderr.readlines():
				output += line
		results = outputParser.parseGenericOutput(output, fields)
		if results != None:
			results = [result for result in results if len(result) > 0]
			results = results[0] if len(results) == 1 else results
		return results