# puppet/modules/nfs/manifests/init.pp
# Taken from Puppet 2.7 Cookbook by John Arundel, page 215

class nfs ($mustuse=false){	
	if ($mustuse){
		package { "nfs-kernel-server": ensure	=> installed }
		service { "nfs-kernel-server":
			ensure		=> running,
			enable		=> true,
			hasrestart 	=> true,
			require		=> Package["nfs-kernel-server"],
		}
		file { "/etc/exports.d":
			ensure		=> directory,
		}
		exec { "update-etc-exports":
			command		=> "/bin/cat /etc/exports.d/* > /etc/exports",
			notify		=> Service["nfs-kernel-server"],
			refreshonly	=> true,
		}
	}
	else{
		if defined(Package['nfs-kernel-server']){
			service { "nfs-kernel-server": ensure 	=> stopped }
		}		
	}

	define share($path, $allowed, $options="bg, nolock, noatime"){
		include nfs

		file { $path:
			ensure 		=> directory,
		}
		file { "/etc/exports.d/${name}":
			content		=> "${path} ${allowed} (${options})\n",
			notify		=> Exec["update-etc-exports"],
		}
	}


}