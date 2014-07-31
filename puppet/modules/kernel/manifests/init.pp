class kernel(	$dbpath	= ["/data", "/data/db"],
				$ulimit	= 64000,
			){
	class { "atime": dbpath => $dbpath }
	class { "filedescriptor": ulimit => $ulimit }
	include hugepages, numa, readahead, ntp

	class atime( $dbpath="/data/db" ) {
		notice("\t\t\tDisabling atime doesn't work at the moment. We need to figure out how to go into /etc/fstab and surgically add (noatime, nodiratime) to the filesystem of ${dbpath}")
	}

	class filedescriptor($ulimit=64000) {
		file { "/etc/sysctl.conf":
			ensure	=> file,
		}
		file_line { "systemlimits":
			path 	=> "/etc/sysctl.conf",
			line 	=> "fs.file-max = ${ulimit}",
			require	=> File["/etc/sysctl.conf"],
		}
		file { "/etc/security/limits.conf":
			ensure	=> file,
		}
		file_line { $lines:
			path 	=> "/etc/security/limits.conf",
			line 	=> $name,
			require	=> File["/etc/security/limits.conf"],
		}
		notice("\t\tFiledescriptor limit increased to ${ulimit} BUT I think you have to restart the system")
	}

	class hugepages {
		file { "/sys/kernel/mm/transparent_hugepage/enabled":
			ensure	=> file,
		}
		exec { "neverhugepages":
			command		=> "/bin/echo never > /sys/kernel/mm/transparent_hugepage/enabled",
			require		=> File["/sys/kernel/mm/transparent_hugepage/enabled"],
		}
		notice("\t\tI think I disabled huge pages but you should also restart the system")
	}

	class numa {
		notice("\t\t\tI'd do something with NUMA but I'm not sure what that is so far")
	}

	class readahead ($ra=32){
		notice("\t\tSetting the readahead should be easy ... right?")
		$blockdevs = ["/dev/sda", "/dev/sda1", "/dev/sda2", "/dev/sda5"]
		setra { $blockdevs:
			ra 			=> $ra,
		}
		define setra($ra) {
			exec { "/sbin/blockdev --setra ${ra} ${name}": }
		}
		notice("\t\tHA! It's not. Right now all the devices are hard coded :(")
	}

	class ntp {
		# This is actually taken from puppetlabs, at:
		# http://docs.puppetlabs.com/learning/modules1.html
		case $operatingsystem {
			centos, redhat: {
				$service_name = 'ntpd'
			}
			debian, ubuntu: {
				$service_name = 'ntp'
			}
		}

		package { 'ntp':
			ensure => installed,
		}
		service { $service_name:
			ensure    => running,
		}
	}
}