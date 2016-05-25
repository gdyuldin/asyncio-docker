# -*- mode: ruby -*-
# vi: set ft=ruby :

$script = <<SCRIPT
sudo tee /etc/apk/repositories > /dev/null <<EOF
http://nl.alpinelinux.org/alpine/v3.3/main
http://nl.alpinelinux.org/alpine/edge/main
http://nl.alpinelinux.org/alpine/edge/community
EOF

sudo apk update
sudo apk add docker && \
  sudo adduser ${USER} docker
  sudo adduser ${USER} root
  sudo service docker start

sudo apk add make python3 && \
    sudo python3 -m ensurepip && \
    sudo rm -r /usr/lib/python*/ensurepip && \
    sudo pip3 install --upgrade pip setuptools && \
    sudo pip3 install virtualenv

cd /vagrant && \
    make install

tee /home/vagrant/.pypirc > /dev/null <<EOF
[distutils]
index-servers =
    pypi
    pypitest

[pypitest]
repository = https://testpypi.python.org/pypi
username = adaptivdesign

[pypi]
repository = https://pypi.python.org/pypi
username = adaptivdesign
EOF

SCRIPT


# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(2) do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://atlas.hashicorp.com/search.
  config.vm.box = "maier/alpine-3.3.1-x86_64"

  # Disable default share if not using shared folders so Vagrant will not block attempting to mount the volume.
  config.vm.synced_folder '.', '/vagrant', type: "nfs"

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  config.vm.network "private_network", ip: "192.168.100.10"

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant.
  config.vm.provider "virtualbox" do |vb|
     vb.memory = "1024"
  end

  config.vm.provision "shell", inline: $script, privileged: false

end
