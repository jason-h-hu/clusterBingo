ClusterBingo
Version 0.1
Jason Hu

Table of Contents
1. Background
2. Use
3. Architecture
4. Bugs
5. Manifests


1. BACKGROUND
------------------------------------------------------------------------------
	ClusterBingo is a way of provisioning Puppet master-agent configurations
	(which in turn are used to provision clusters of machines). This makes use
	of extensive python libraries--paramiko, to organize ssh connections, and
	argparse to parse command line arguments. 
------------------------------------------------------------------------------

2. USE
------------------------------------------------------------------------------
	RUNNING CLUSTER BINGO
		1.	ensure that puppet is installed, as well as paramiko python library
		2.	get a list of ip addresses for all the machines you want to manage
				- get the passwords, usernames, and rsa keys as necessary
		3. 	Start up the file app.py in the file bingo
		4.	follow the instructions in the interface

	ADDING MODULES
		1. 	Create a puppet manifest called init.pp
			See the puppet documentation on creating new modules.

		2.	Write a directory with the structure
			bingo/
			  modules/
				moduleName/
					manifests/
						init.pp

					files/
		
			If you save it in the modules, in the clusterBingo directory, 
			then it'll automatically find the module.
------------------------------------------------------------------------------

3. ARCHITECTURE
------------------------------------------------------------------------------
	Functionality is partitioned into frontend and backend python modules, with
	the app.py file coordinating between the two of them. In the backend, the
	master.py class is in charge of the master machine--this is assumed
	to be the machien that ClusterBingo is running on. It'll clear out 
	certificates and start up the puppetmaster. 

	The backend also parses the configuration file, maintains a pool of ssh
	connections via paramiko, and manages the manifest.

	When a machine is entered--either through the config file or through
	user input, then the "setMachine" method is called. This creates an
	sshThread which ssh's into the machine, sets up puppet, and then the
	thread and the master coordinate the SSL verification.

	The front end is largely in charge of user input from the command line. 

------------------------------------------------------------------------------

4. BUGS
------------------------------------------------------------------------------
	1. 	This only works for a very, very limited subset of operating systems
	2. 	There's no robust way of finding the os or package manager--right now
		it guess and checks against a known list. 
	3.	Right now it can't take input from a configuration file, forcing
		input through the command line interface. 
	4. 	A lot of paths are hard coded
	5. 	A lot of ssh parameters, like rsa key, username, ipaddress, and
		passwords are hardcoded
	6. 	A lot of functionality is reliant on shell commands, which don't
		fail gracefully and can take down the program. 
	7.	More bugs/severe limitations are noted throughout the code. 
------------------------------------------------------------------------------


5. MANIFESTS
------------------------------------------------------------------------------
All the modules I'm using are based off of the production notes from MongoDB. 
(http://docs.mongodb.org/manual/administration/production-notes/). I highly 
recommend checking each module to ensure it does what you want it to do before
use. 

Here's a list of the what each of the manifests do.

MODULE				DESCRIPTION
mongodb				installs monogodb, and ensures the directroy /data exists
swap				creates a swap file of 2x memory
nfs					disables nfs
kernel
	filedescriptor	changes the file descriptor to 64000
	readahead		changes the readahead to 32
	ntp				turns on ntp
------------------------------------------------------------------------------
