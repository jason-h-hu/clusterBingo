import re
import os.path
import paramiko
import app
import sys
import socket

"""
A helper method for printing
"""
def output(text, err=0):
	if app.verbose or err>0:
		if isinstance(text, str):
			sys.stdout.write( text )
		elif isinstance(text, dict):
			sys.stdout.write( json.dumps(text, indent=1).replace("{", "").replace("}\n", "") )

def generateJSONName(path):
	if isinstance(path, str) or isinstance(path, unicode):
		path = str(path.replace("\n", ""))
		path = path.replace(" ","")
		if not (re.search(".*\.json", path) or re.search(".*\.JSON", path)):
			path += ".json"	
		return path

def findJSONFile(path):
	path = generateJSONName(path)
	if path != None:
		if os.path.exists(path):
			if os.path.isfile(path):
				return path 
	return None

def cleanupWhiteSpace(terminalInput):
	return re.sub(r"\s+", "", terminalInput)

def cleanupAndSplitTerminalInput(terminalInput):
	terminalInput = terminalInput.replace("\n", "")
	terminalInput = re.split(",*\s+", terminalInput)
	return terminalInput

def isValidIPInput(triplet):
	success = True	
	if len(triplet) > 1 and isinstance(triplet, list):
		test = paramiko.SSHClient()
		test.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		try:
			if len(triplet) > 2:
				test.connect(triplet[1], username=triplet[0], key_filename=triplet[2])
				test.close()
			else:
				test.connect(triplet[1], username=triplet[0])
				test.close()
		except paramiko.AuthenticationException:
			success = False
			output(str(triplet) + " wasn't a valid username, IP address, and rsa key. Authentication Exception\n")
		except socket.error, e:
			success = False
			output(str(triplet) + " wasn't a valid username, IP address, and rsa key. Socket Error.\n")
		except paramiko.ssh_exception.SSHException:
			success = False
			output(str(triplet) + " wasn't a valid username, IP address, and rsa key. SSH Exception. \n")
	else:
		success = False
		output(str(triplet) + " doesn't follow the proper form of [username] [ip address] [rsa key path]\n")
	return success

