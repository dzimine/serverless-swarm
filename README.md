# Serverless with Docker, Swarm, and StackStorm.


## Setting up

### 1. Vagrant

I use Vagrant to create a repeatable local dev environment, representable of one at AWS or DigitalOcean. 
Inspired by [6 practices for super smooth Ansible experience](http://hakunin.com/six-ansible-practices). This will set 3 boxes, named `st2.my.dev`, `node-1.my.dev`, and `node-2.my.dev`, with ssh access configured for root. Set up steps:

1. Generate  a pairs of SSH keys:  `~/.ssh/id_rsa`, `~/.ssh/id_rsa.pub`  (to use different keys, update the call to `authorize_key_for_root` in `Vagrantfile` accordingly).

2. Configure ssh client like this `~/.ssh/config`:

	```
	# ~/.ssh/config
	# For vagrant virtual machines
	# WARN: don’ do this for production!
	Host 192.168.80.* *.my.dev
	   StrictHostKeyChecking no
	   UserKnownHostsFile=/dev/null
	   User root
	   LogLevel ERROR
	```

3. Install [vagrant-hostmanager](https://github.com/devopsgroup-io/vagrant-hostmanager).

4. Run `vagrant up`. You will need to type in the password to let Vagrant update `/etc/hosts/`. 

5. Profit. Log in as a root with `ssh st2.my.dev`, `ssh node-1.my.dev`, and `ssh node-2.my.dev`.

Troubles: Due to [hostmanager bugs](https://github.com/devopsgroup-io/vagrant-hostmanager/issues/159), `/etc/hosts` on the host machine may not be cleaned up. Clean it up by hands. Or use `sudo vagrant up` and `sudo vagrant destroy` to avoid this.


### 2. Ansible
