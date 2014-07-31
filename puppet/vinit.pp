package { "puppetmaster":
	require 	=> Exec['apt-get update'],
	ensure		=> present
}

package { "vim":
	require 	=> Exec['apt-get update'],
	ensure		=> present
}