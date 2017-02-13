# -*- mode: ruby -*-
# vi: set ft=ruby :

require_relative './scripts/authorize_key'

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"


domain    = ENV['DOMAIN'] ? ENV['DOMAIN'] : "my.dev"
ip_base   = ENV['IP_BASE'] ? ENV['IP_BASE'] : "192.168.80"

nodes = { # [ count, ip block start, vcpu, mem ]
  'node'  => [2, 101, 2, 1024],
  'st2'   => [1, 200, 2, 2048],
}


Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/trusty64"
  authorize_key_for_root config, '~/.ssh/id_rsa.pub'

  # Hostmanager config. See https://github.com/devopsgroup-io/vagrant-hostmanager
  config.hostmanager.enabled = true
  config.hostmanager.manage_host = true
  config.hostmanager.manage_guest = true
  config.hostmanager.ignore_private_ip = false
  config.hostmanager.include_offline = true

  nodes.each do |prefix, (count, ip_start, vcpu, vmem)|
    count.times do |i|
      hostname = (count == 1 ? prefix : prefix+"#{i+1}")
      # puts "Provisioning a node %s: %s vcpu / %s Mb" % [hostname, vcpu, vmem]
      config.vm.define "#{hostname}" do |box|
        box.vm.hostname = "#{hostname}.#{domain}"
        box.vm.network :private_network, ip: "#{ip_base}.#{ip_start+i}", :netmask => "255.255.255.0"

        # Run the Shell Provisioning Script file
        # box.vm.provision :shell, :path => "#{prefix}.sh"

        box.vm.provider :virtualbox do |vbox|
          vbox.customize ["modifyvm", :id, "--memory", vmem]
          vbox.customize ["modifyvm", :id, "--cpus", vcpu]

          # Use faster paravirtualized networking
          # vbox.customize ["modifyvm", :id, "--nictype1", "virtio"]
          # vbox.customize ["modifyvm", :id, "--nictype2", "virtio"]
        end
      end
    end
  end
end
