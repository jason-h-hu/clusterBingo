import argparse
import json
from bingo.backend.utils import *

# This class is in charge of parsing the command line arguments
# as well as any configuration files passed in.

# Right now this is completely half-baked. It needs to be able to 
# parse a file for ip addresses, passwords, rsa keys, usernames. 

# It should also be able to parse a list of modules, to know what
# to include, as well as it should probably be able to take in 
# arbitrary puppet declarations. 

class ConfigParser(object):
	"""docstring for ConfigParser"""
	def __init__(self, backend):
		super(ConfigParser, self).__init__()
		self.backend = backend
		
	# For a list of possible ip addresses with accompanying information,
	# this tries to create ssh connections in the backend
	def addIPTuple(self, ipTuple):
		ip = ipTuple["ip"] if "ip" in ipTuple else "127.0.0.1"
		username = ipTuple["username"] if "username" in ipTuple else "root"
		password = ipTuple["password"] if "password" in ipTuple else "password"
		rsaKey = ipTuple["rsa"] if "rsa" in ipTuple else "/.rsa"
		self.backend.setMachine(ip=ip, username=username, password=password, rsa=rsa)

	# This should open up the file and look for ip addresses. 
	def parseConfigFile(self, configFilePath):
		output("Looking for " + configFilePath + "\n")
		configFilePath = ensureValidJSONFile(configFilePath)

		if configFilePath != None:
			config = json.load(open(configFilePath))
			if "ssh" in config:
				if isinstance(config["ssh"], list):
					for ipTuple in config["ssh"]:
						self.addIPTuple(ipTuple)
				elif isinstance(config["ssh"], dict):
					self.addIPTuple(config["ssh"])

		else:
			output("Couldn't parse the config file!\n")

	# In order to know what files to look for, and what to do with them,
	# cluster bingo should take commands from the command line when it's starting up.
	# This should parse those commands
	def parseCommandLineArguments(self):
		output("Parsing command line arguments ... \n")
		parser = argparse.ArgumentParser(description="Checks that various system configurations are tuned properly")
		parser.add_argument("--config",			"-c", 	help="A JSON file that describes the machines we want to use, the list of core checks we want to run, and a list of optional custom checks. It also can have a field for the desired settings we want to see.")
		# TODO: Add option for verbose, ip address, manifests, etc. 													<------------------TODO
		# Anything able to be done in the cofnig file should be able to 
		# be done in the command line arguments


		args = parser.parse_args()

		if args.config != None:
			self.parseConfigFile(args.config)
		output("... done!\n")