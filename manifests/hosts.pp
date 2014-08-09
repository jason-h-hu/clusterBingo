file_line { "hosts":
	path 	=> "/etc/hosts",
	line 	=> "${ip}\t${hostname}",
	require	=> File["/etc/hosts"],
}