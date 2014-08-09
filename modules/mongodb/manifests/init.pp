
# puppet/modules/mongodb/manifests/init.pp

class mongodb($dbpath=["/data", "/data/db"]) {
	package { 'mongodb':
		ensure	=> present,
	}
	file { $dbpath:
		ensure	=> directory,
	}
}