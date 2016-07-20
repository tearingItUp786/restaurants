# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|

# shell script to run so we have installed all necessary packages
  config.vm.provision :shell, path: "pg_config.sh"
# the distro we are running
  config.vm.box = "ubuntu/trusty32"
# which port to forward to
  config.vm.network "forwarded_port", guest: 5000, host: 5000

end
