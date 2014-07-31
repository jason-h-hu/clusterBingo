# puppet/modules/os/manifests/init.pp

class os {
	notice("The operating system is ${operatingsystem} and its family is ${operatingsystemrelease}")
	$knownOS = ['MacOS', 'RedHat', 'Debian', 'Ubuntu', 'Fedora', 'Windows', 'Solaris']
	if !($operatingsystem in $knownOS) {
		fail("Unrecognized operating system of ${operatingsystem} for webserver")
	}
}