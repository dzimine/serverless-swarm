# Serverless with Docker, Swarm, and StackStorm.

This is my playgrond to prototype "serverless" with Swarm and StackStorm.

## Setting Up

All you need to get a swarm cluster running **conviniently**, per [Swarm tutorial](https://docs.docker.com/engine/swarm/swarm-tutorial/).

### 1. Provision machines (with Vagrant)
First we need to provision machines where Swarm will be deployed. I'll use thee boxes:

| Host          | Role            |
|---------------|-----------------|
| st2.dev.net   | Swarm manager, Docker Registry, StackStorm     |
| node1.dev.net | Swarm worker    | 
| node2.dev.net | Swarm worker    |

Roles are described as code in [`inventory`]() file. Dah, this proto setup is for play, not for production.

Vagrant is used to create a repeatable local dev environment, with convinience tricks inspired by [6 practices for super smooth Ansible
experience](http://hakunin.com/six-ansible-practices). This will set 3 boxes,
named `st2.my.dev`, `node1.my.dev`, and `node2.my.dev`, with ssh access
configured for root. Set up steps:

1. Generate  a pair of SSH keys:  `~/.ssh/id_rsa`, `~/.ssh/id_rsa.pub` (to
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

3. Install [vagrant-hostmanager](https://github.com/devopsgroup-io/vagrant-hostmanager):
    ```
    vagrant plugin install vagrant-hostmanager
    ```

4. Run `vagrant up`. You will need to type in the password to let Vagrant
update `/etc/hosts/`.

5. Profit. Log in as a root with `ssh st2.my.dev`, `ssh node1.my.dev`, and
`ssh node2.my.dev`.

Troubles: Due to [hostmanager bugs](https://github.com/devopsgroup-io/vagrant-
hostmanager/issues/159), `/etc/hosts` on the host machine may not be cleaned
up. Clean it up by hands.


### 2. Deploy Swarm cluster
Ok, machines are set up. Let deploy a 3-node Swarm cluster.

1. Create Swarm cluster:

    ```
    ansible-playbook playbook-swarm.yml -vv -i inventory
    ```
2. Set up the [local Docker Registry]():

	```
	ansible-playbook playbook-registry.yml -vv -i inventory
	```
3. Add [Swarm visualizer](https://github.com/ManoMarks/docker-swarm-visualizer) for a nice eye-candy. Run this command on Swarm master.

	```
	# ATTENTION! 
	# Run this on Swarm master, st2.my.dev
	
	docker service create \
	--name=viz \
   --publish=8080:8080/tcp \
   --constraint=node.role==manager \
   --mount=type=bind,src=/var/run/docker.sock,dst=/var/run/docker.sock \
   manomarks/visualizer
   ```

   Connect to Visualizer via [http://st2.my.dev:8080](http://st2.my.dev:8080) and see this one server there.


### 3. Install StackStorm:

```sh
# Install requirements for ansible-st2 playbooks
ansible-galaxy install -r ansible-st2/roles/mistral/requirements.yml
    
# Run ansible to install StackStorm
ansible-playbook playbook-st2.yml -i inventory
    
```

**Pat me on a back, infra is done!** We got three nodes with docker, running as Swarm, with local Registry, and StackStorm to rule them all.

## Play time!

### 1. Running app in plain Docker

The apps are placed in (drum-rolls...) `./apps`. 
By the virtue of default Vagrant share, it is available inside
all VMs at `/vagrant/apps`.

Login to a VM. Any node would do as docker is installed on all. 

    ssh node1.my.dev

1. Build an app:

    ```
    cd /vagrant/apps/encode
    docker build -t encode . 
    ```
2. Push the app to local docker registry:
    
    ```
    docker tag encode st2.my.dev:5000/encode
    docker push st2.my.dev:5000/encode
    
    # Inspect the repository
    curl --cacert /etc/docker/certs.d/st2.my.dev\:5000/registry.crt https://st2.my.dev:5000/v2/_catalog
    curl --cacert /etc/docker/certs.d/st2.my.dev\:5000/registry.crt -X GET https://st2.my.dev:5000/v2/encode/tags/list
    ```
3. Run the app: 
    
    ``` 
    docker run --rm -v /vagrant/share:/share \
    st2.my.dev:5000/encode -i /share/li.txt -o /share/li.out --delay 1
    ```
	Reminders: 
	
	* `--rm` to remove container once it exits. 
	* `-v` maps `/vagrant/share` of Vagrant VM to `/share` inside the container.
	  This acts as a shared storage across Swarm VMs as `/vagrant/share` maps to the host machine. On AWS we need to figure good shared storage alternative.
	* `-i`, `-o`, `--delay` are app parameters.


4. Login to another node, and run the container app from there. It will download the image and run the app.

### 2. Swarm is coming to town
Run the job with swarm command-line: 

```
docker service create --name job2 \
--mount type=bind,source=/vagrant/share,destination=/share \
--restart-condition none st2.my.dev:5000/encode \
-i /share/li.txt -o /share/li.out --delay 20
```

Run it a few times, enjoy seeing them pile up in visualizer, just be sure to give a different job name.

### 3. Now repeat with StackStorm
Run StackStorm pipeline pack.

Install `pipeline` pack. Hackish way is to symlink it in place:

```
ln -s /vagrant/pipeline/ /opt/stackstorm/packs/
st2clt reload
# check the action is in place and ready
st2 action list --pack=pipeline
```

To run the pack's unit tests: 

```
# Dang I need ST2 
git clone --depth=1 https://github.com/StackStorm/st2.git /tmp/st2
# Run unit tests now
ST2_REPO_PATH=/tmp/st2 /opt/stackstorm/st2/bin/st2-run-pack-tests -p /opt/stackstorm/packs/pipeline
```

Run the job via stackstorm: 

```
st2 run -a pipeline.run_job \
image=st2.my.dev:5000/encode \
mounts='["type=bind,source=/vagrant/share,target=/share"]' \
args="-i","/share/li.txt","-o","/share/test.out","--delay",3
```

To clean-up jobs (we've got a bunch!):

```
docker service rm $(docker service ls | grep "job*" | awk '{print $2}'
```

### 4. Stitch with Workflow
To run the workflow that executes multiple actions:

```
st2 run -a pipeline.pipe \
input_file=/share/li.txt output_file=/share/li.out \
parallels=4 delay=10
```
Use StackStorm UI at [https://st2.my.dev](https://st2.my.dev) to inspect workflow execution.

TODO: Continue expanding the workflow to make more representative.