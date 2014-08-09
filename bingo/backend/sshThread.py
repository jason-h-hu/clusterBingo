import paramiko
import threading
import re
from bingo.backend.utils import * 

# This class takes care of connecting with a machine and ensuring
# it has puppet and also setting up the SSL certification.
class sshThread(threading.Thread):
	# TODO: While there's no real way around hardcoding these values without more
	# information, I think the rsa key shouldn't be hardcoded--there must be
	# a way to find where most RSA keys are stored														<------------------TODO
	def __init__(self, backend, ip="172.28.128.37", username="vagrant", password="vagrant", rsa="/vagrant/JASONHU.cer", update=False):
		super(sshThread, self).__init__()
		self.update = update
		self.backend = backend
		self.ip = ip
		self.username = username
		self.rsa = rsa

		output("Establishing SSH connection to " + ip + " ...")
		self.ssh = paramiko.SSHClient()
		self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.ssh.connect(str(self.ip), username=str(self.username), password=str(password), key_filename=str(self.rsa))
		output(" success!\n")

	# Helper method to run a command--warning, it will throw exceptions
	def runCommand(self, command, shell=False):
		command = "sudo bash --login -c \'" + command + "\'" if shell else command
		stdin, stdout, stderr = self.ssh.exec_command(command)
		output = []
		for line in stdout.readlines():
			output.append(line)
		return "".join(output)

	# Sometimes, commands need to be run after the bashsrc has been booted up--
	# this does that, and then runs the command
	def runInSession(self, command, shell=False):
		channel = self.ssh.get_transport().open_session()
		channel.get_pty()
		command = "sudo bash --login -c \'" + command + "\'" if shell else command
		channel.exec_command(command)
		output = ""
		bufferSize = 512
		frag = channel.recv(bufferSize)
		while frag:
			output += frag
			frag = channel.recv(bufferSize)
		return output

	# This ensures a program is installed
	# program is the name of the program, aka the package name
	# command is the name of the command run from the terminal
	# Oftentimes these are the same thing.
	def ensureInstalled(self, program, command=""):
		output("\tLooking for " + program + " ... ")
		if len(command) == 0:
			command = program
		path = self.runCommand("which " + command)

		# 2. If the program is currently not installed
		if (len(path) < 1):
			output(" can't find it. Starting to install ... ")

			# 2.a Call the appropriate package manager
			installCommand = "sudo " + self.packageManager + "  -y install " + program
			msg = self.runInSession(installCommand)
			path = re.sub("\n", "", self.runCommand("which " + command))
			output("installed " + program + " at " + path + "!\n")
			
		else:
			output("found it!\n")

	# This ensures puppet is installed
	def ensurePuppet(self):

		output("Installing programs ...\n")
		# if self.update:
		if True:
			output("\tRunning sudo " + self.packageManager + " update\n")
			msg = self.runInSession("sudo " + self.packageManager + "  -y update")

		programs = ["puppet", "facter"]
		for program in programs:
			self.ensureInstalled(program)

		output("Finished installation!\n")

	# This ensures that we've killed previous puppets, freed up
	# certificates and pids, configured hosts with the
	# master address
	def configurePuppet(self):
		output("Editing puppet configurations ...\n")

		# 0. Find and kill all instances
		output("\tKilling all running puppets ... \n")
		processes = self.runCommand("ps -e | grep puppet")
		processes = [re.split("\s+", line) for line in processes.split("\n")]
		for process in processes:
			if "puppet" in process:
				for i in range(len(process)):
					if (re.match("^\d+$", process[i])):
						self.runCommand("kill " + process[i])
						output("\t\tKilled " + process[i] + "\n")

		# 1. Clear all certificates & .pid's
		output("\tClearing pre-existing SSL certificates ... \n")
		commands = ["rm -r /etc/puppet/ssl", "rm -r /var/lib/puppet/ssl", "rm -r /var/run/puppet/*.pid"]
		for command in commands:
			self.runCommand("sudo " + command)

		# 2. Check whether the current ip address is in /etc/hosts
		output("\tConfiguring /etc/hosts ... \n")
		hostMissing = True
		hosts = self.runCommand("cat /etc/hosts")
		for line in hosts.split("\n"):
			parsedLine = re.split("\s+", line)
			ipAddress = parsedLine[0]
			if (isIPAddress(ipAddress)):
				for i in range(1, len(parsedLine)):
					hostname = re.sub("\s+", "", parsedLine[i])
					if hostname == self.backend.hostname:
						output("hostname: " + self.backend.hostname + " already here!\n")
						hostMissing = False

		# 3. If not, insert it in, with the custom host name
		if (hostMissing):
			command = "echo \"" + self.backend.ipaddress + "\t" + self.backend.hostname + "\" >> /etc/hosts"
			msg = self.runInSession(command, shell=True)
			output("added " + self.backend.hostname + " to list of known hosts!\n")

	# Again, this is a really unsophisticated way of finding the package manager.
	def findPackageManager(self):
		packageManagers = ["apt-get", "yum", "rpm"]
		for packageManager in packageManagers:
			path = self.runCommand("which " + packageManager)
			if (len(path) > 1):
				return re.sub("\s+", "", path)
		return ""

	def initializeMachine(self):
		# Find the hostname ang get the package manager
		self.hostname = re.sub("\s+", "", self.runInSession('hostname')) 
		self.packageManager = self.findPackageManager()
		if len(self.findPackageManager()) < 1:
			output("ERROR: Couldn't find a package manager in " + self.hostname + ", exiting out\n")
			sys.exit(0)

	def runPuppet(self):
		output("Running puppet on " + self.hostname + "\n")
		command = "sudo puppet agent --listen --server " + self.backend.hostname
		msg = self.runInSession(command, shell=True)
		self.backend.certify(self)

	def run(self):
		self.ensurePuppet()
		self.configurePuppet()
		self.runPuppet()