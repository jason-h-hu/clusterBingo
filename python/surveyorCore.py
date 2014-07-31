import json
import subprocess
import re
import sys
import argparse
import os.path
import threading
import socket
import paramiko
import outputParser 

class surveyor(object):
	def __init__(self, ssh, checkDict={}):
		super(surveyor, self).__init__()
		self.ssh = ssh

	def survey(self):
		pass

	def parse(self):
		pass

	def check(self):
		pass

class surveyorCore(object):

	def __init__(self, ssh):
		super(surveyorCore, self).__init__()
		self.ssh = ssh
		
	def blockdev(self):
		# This is really strange. We have to bend over backward
		# because of tty permisions, for sudo-ing over paramiko
		chan = self.ssh.get_transport().open_session()
		chan.get_pty()
		chan.exec_command("sudo blockdev --report")
		output = ""
		frag = chan.recv(1024)
		while frag:
			output += frag
			frag = chan.recv(1024)
		parsedOutput = outputParser.parseSpaceSeparatedTableOutput(output)
		queries = ["RA", "Device"]
		results = []
		for po in parsedOutput:
			result = {}
			for field in po:
				if field in queries:
					result[field] = po[field]
			if len(result) > 0:
				results.append(result)
		return results

	def cpu(self):
		stdin, stdout, stderr = self.ssh.exec_command("cat /proc/cpuinfo")
		output = ""
		for line in stdout.readlines():
			output += line
		output = outputParser.parseKeyValueList(output)

		results = {}
		queries = ["cpu", "stepping", "cache_alignemnt", "cache size", "model", "processor"]
		for query in queries:
			if query in output:
				results[query] = output[query]
		return results

	def filesystem(self):
		stdin, stdout, stderr = self.ssh.exec_command("df -T")
		output = [re.split("\s+", line) for line in stdout.readlines()]
		output = [line for line in output if len(line) > 6]
		labels = output[0]
		
		for i in range(len(labels)-1):
			if re.match("[Mm]ounted", labels[i]):
				if re.match("[Oo]n", labels[i+1]):
					labels[i] += labels[i+1]
					labels.pop(i+1)
					break

		returnVal = {} 
		queries = ["Use%", "Used", "Mountedon", "Filesystem", "Type"]
		for i in range(1, len(output)):
			line = output[i]
			for j in range(len(line)):
				if labels[j] in queries:
					returnVal[labels[j]] = line[j]
		return returnVal

	def kernel(self):
		stdin, stdout, stderr = self.ssh.exec_command("uname -r")
		output = ""
		for line in stdout.readlines():
			output += line
		return outputParser.cleanup(output)

	def largePages(self):
		stdin, stdout, stderr = self.ssh.exec_command("cat /proc/meminfo | grep Huge")
		output = ""
		for line in stdout.readlines():
			output += line
		output =  outputParser.parseKeyValueList(output)
		queries = ["Hugepagesize"]
		results = {}
		for query in queries:
			if query in output:
				results[query] = output[query]
		return results

	def raid(self):
		stdin, stdout, stderr = self.ssh.exec_command("cat /proc/mdstat")
		output = ""
		for line in stdout.readlines():
			output += line
		return outputParser.parseKeyValueList(output)

	def ssd(self):
		stdin, stdout, stderr = self.ssh.exec_command("ls /sys/block")
		fsystems = [line.replace("\n", "") for line in stdout.readlines()]
		returnVal = {}
		for fs in fsystems:
			stdin, stdout, stderr = self.ssh.exec_command("cat /sys/block/" + fs + "/queue/rotational")	
			output = ""
			for line in stdout.readlines():
				output += line
			if len(output) > 0:
				returnVal[fs] = (int(output) == 1)
		return returnVal

	def swapSpace(self):
		stdin, stdout, stderr = self.ssh.exec_command("cat /proc/swaps")
		output = [re.split("\s+", line) for line in stdout.readlines()]
		labels = output[0]

		returnVal = []
		for i in range(1, len(output)):
			line = output[i]
			swapSetting = {}
			for j in range(len(line)):
				swapSetting[labels[j]] = line[j]
			returnVal.append(swapSetting)
		returnVal = returnVal if len(returnVal) > 0 else None
		return returnVal


	"""
	This will gather the specified system check and return it as a JSON object 

	check: a string, treated as an enumerated type, to decide which method we want to call. 
	ssh: a paramiko SSHClient instance
	"""
	def survey(self, check):
		if check == "blockdev":
			return self.blockdev()
		elif check == "cpu":
			return self.cpu()
		elif check == "filesystem":
			return self.filesystem()
		elif check == "kernel":
			return self.kernel()
		elif check == "largePages":
			return  self.largePages()
		elif check == "raid":
			return self.raid()
		elif check == "ssd":
			return self.ssd()
		elif check == "swapSpace":
			return self.swapSpace()
		return None
