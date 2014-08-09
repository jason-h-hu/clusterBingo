# puppet/modules/swap/manifests/init.pp

class swap {

	$memory = split($::memorysize, '[.]')
	$desiredswap = $memory[0]*2
	$paths = [ "/bin/", "/sbin/" , "/usr/bin/", "/usr/sbin/" ]

	$swap = split($::swapsize, '[.]')
	$swapsize = $desiredswap - $swap[0]
	$swapfile = '/mnt/swaplvm'
	if $swapsize > 0 {
		notice("we still need ${swapsize}.${swap[1]}")
		exec { 'dd':
			path 		=> $paths,
			command 	=> "/bin/dd if=/dev/zero of=${swapfile} bs=1M count=${swapsize}",
			creates 	=> $swapfile,
		}
		exec { 'mkswap':
			path 		=> $paths,
			require 	=> Exec['dd'],
			command 	=> "/sbin/mkswap -f ${swapfile}",
			unless  	=> "/sbin/swapon -s | grep ${swapfile}",
		}
		exec { 'swapon':
			path 		=> $paths,
			require		=> Exec['mkswap'],
			command		=> "/sbin/swapon ${swapfile}",
		}
	}
}