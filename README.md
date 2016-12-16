# Serverless with Docker, Swarm, and StackStorm.


## Setting up

### 1. Vagrant

I use Vagrant to create a repeatable local dev environment, representable of
one at AWS or DigitalOcean.  Inspired by [6 practices for super smooth Ansible
experience](http://hakunin.com/six-ansible-practices). This will set 3 boxes,
named `st2.my.dev`, `node1.my.dev`, and `node2.my.dev`, with ssh access
configured for root. Set up steps:

1. Generate  a pairs of SSH keys:  `~/.ssh/id_rsa`, `~/.ssh/id_rsa.pub`  (to
use different keys, update the call to `authorize_key_for_root` in
`Vagrantfile` accordingly).

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

3. Install [vagrant-hostmanager](https://github.com/devopsgroup-io/vagrant-
hostmanager).

4. Run `vagrant up`. You will need to type in the password to let Vagrant
update `/etc/hosts/`.

5. Profit. Log in as a root with `ssh st2.my.dev`, `ssh node1.my.dev`, and
`ssh node2.my.dev`.

Troubles: Due to [hostmanager bugs](https://github.com/devopsgroup-io/vagrant-
hostmanager/issues/159), `/etc/hosts` on the host machine may not be cleaned
up. Clean it up by hands.


### 2. Ansible
I use Ansible to deploy the software components on the nodes.

1. Create Swarm cluster:

    ```
    ansible-playbook playbook-swarm.yml -i inventory
    ```

2. Install StackStorm:

    ```sh
    # Install requirements for
    ansible-galaxy install -r ansible-st2/roles/mistral/requirements.yml
    
    # Run ansible to install StackStorm
    ansible-playbook playbook-st2.yml -i inventory
    
    ```

### 3. Running app in Docker

The apps are placed in (drum-rolls...) `./apps`. 
By the virute of default Vagrant share, it is available inside
all VMs at `/vagrant/apps`.

Login to a VM. Any would do as docker is installed on all. 

    ssh st2.my.dev

Build an app:

    cd /vagrant/apps/encode
    docker run --rm -v /vagrant/share:/share dz/

Run an app: 

    docker run --rm -v /vagrant/share:/share \ 
    dz/encode -i /share/li.txt -o /share/li.out --delay 3

Reminders: 

* `--rm` to remove container once it exits. 
* `-v` maps `/vagrant/share` of Vagrant VM to `/share` inside the container.
  This acts as a shared storage across Swarm VMs as `/vagrant/share` maps to the host machine. On AWS we need to figure good shared storage alternative.


## Coming up 
* Setting up repository

```
# Generate certificate, use st2.my.dev as CN
openssl req -newkey rsa:4096 -nodes -sha256 -keyout certs/domain.key -x509 -days 365 -out certs/domain.crt

# Run repository as a docker container, with certificate.

docker run -d -p 5000:5000 --restart=always --name registry \
  -v `pwd`/certs:/certs \
  -v /vagrant/registry:/var/lib/registry
  -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/registry.crt \
  -e REGISTRY_HTTP_TLS_KEY=/certs/registry.key \
  registry:2

# Copy
# The directory shall match the URL, including PORT.
mkdir -p /etc/docker/certs.d/st2.my.dev:5000
cp certs/registry.crt /etc/docker/certs.d/st2.my.dev:5000/ca.crt
# Restart docker engine

# Try it out
docker pull hello-world
docker tag hello-world st2.my.dev:5000/hello-world
docker push st2.my.dev:5000/hello-world
docker images
docker tag dz/encode st2.my.dev:5000/encode
docker push st2.my.dev:5000/encode

curl --cacert certs/registry.crt -X GET https://st2.my.dev:5000/v2/_catalog
curl --cacert certs/registry.crt -X GET https://st2.my.dev:5000/v2/encode/tags/list

```

	

* Add [Swarm visualizer](https://github.com/ManoMarks/docker-swarm-visualizer). Run it on Swarm, connect at [http://st2.my.dev:8080](http://st2.my.dev:8080):
	
	```
	docker service create \
	--name=viz \
   --publish=8080:8080/tcp \
   --constraint=node.role==manager \
   --mount=type=bind,src=/var/run/docker.sock,dst=/var/run/docker.sock \
   manomarks/visualizer
   ```
* 