exec { "apt-get-update":
	command		=> "/usr/bin/apt-get update"
}

package { "puppetmaster":
	ensure		=> present,
	require		=> Exec["apt-get-update"]
}

package { "python-pip":
	ensure		=> present,
	require		=> Exec["apt-get-update"]
}

exec { "python-dev":
	command		=> "/usr/bin/apt-get install python-dev -y",
	require		=> Package["python-pip"]
}

exec { "download-paramiko":
	command		=> "/usr/bin/pip install paramiko",
	require		=> Exec["python-dev"]
}