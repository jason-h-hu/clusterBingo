class kernel(	$dbpath	= ["/data", "/data/db"],
				$ulimit	= 64000,
			){
	class { "filedescriptor": ulimit => $ulimit }
	include readahead, ntp

	class filedescriptor($ulimit=64000, $softhard=["soft nofile", "hard nofile"]) {
		file { "/etc/sysctl.conf":
			ensure	=> file,
		}
		file { "/etc/security/limits.conf":
			ensure	=> file,
		}
		file_line { "systemlimits":
			path 	=> "/etc/sysctl.conf",
			line 	=> "fs.file-max = ${ulimit}",
			require	=> File["/etc/sysctl.conf"],
		}
		file_line { "securitylimits":
			path 	=> "/etc/security/limits.conf",
			line 	=> "* soft nofile ${ulimit}\n* hard nofile ${ulimit}",
			require	=> File["/etc/security/limits.conf"],
		}
		exec { "sysctl":
			command		=> "/sbin/sysctl -p",
			require		=> File_line["systemlimits"],
		}
		exec { "ulimit":
			command		=> "/bin/bash -c 'ulimit -n ${ulimit}'",
			require		=> Exec["sysctl"],

		}
		notice("\t\tFiledescriptor limit increased to ${ulimit} BUT you have to restart the system")
	}

	class readahead ($ra=32){
		notice("\t\tSetting the readahead should be easy ... right?")
		$blockdevs = ["/dev/sda"]
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