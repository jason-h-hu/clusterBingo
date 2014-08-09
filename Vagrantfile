Vagrant.configure("2") do |config|

  config.vm.provision "shell", inline: "echo Hello"

  config.vm.define "puppet" do |puppetmaster|
    puppetmaster.vm.hostname = "puppet"
    puppetmaster.vm.box = "precise64"
    puppetmaster.vm.network "private_network", type: "dhcp"
    puppetmaster.vm.provision "puppet" do |puppet|
      puppet.manifest_file = "vdefault.pp"
    end
  end


  config.vm.define "agent1" do |agent1|
    agent1.vm.hostname = "agent1"
    agent1.vm.box = "precise64"
    agent1.vm.network "private_network", type: "dhcp"
  end

  config.vm.define "agent2" do |agent2|
    agent2.vm.hostname = "agent2"
    agent2.vm.box = "precise64"
    agent2.vm.network "private_network", type: "dhcp"
  end

  config.vm.define "agent3" do |agent3|
    agent3.vm.hostname = "agent3"
    agent3.vm.box = "precise64"
    agent3.vm.network "private_network", type: "dhcp"
  end

  config.vm.define "agent4" do |agent4|
    agent4.vm.hostname = "agent4"
    agent4.vm.box = "precise64"
    agent4.vm.network "private_network", type: "dhcp"
  end

  config.vm.define "agent5" do |agent4|
    agent4.vm.hostname = "agent4"
    agent4.vm.box = "precise64"
    agent4.vm.network "private_network", type: "dhcp"
  end

end

