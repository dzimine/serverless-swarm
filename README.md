# Serverless framework on Docker, Swarm, and StackStorm

This project came out of a serverless solution for computational genome
annotations (a very exciting topic on it’s own). The emerging serverless
framework begins to look promising for other applications, and may be
interesting to the community.

At a minimum, this serves as a convenient and reliable playground for Docker Swarm, with local Registry and other cool tools, on your dev box.

At best, this may involve into a solid Serverless framework.

At the current state, it is an experimenting ground with working examples that
produce food for thought and more experimenting.

The sample functions and example wordcount map-reduce workflow are here with
instructions of how to run them. The bioinformatic part contains some trade-
secret bits, so it is kept privately and mixed in to run in production. You
are welcome to explore it's orchestration and wiring.

The solution is under active development; your constructive criticism and
contributions are welcome:  [@dzimine](https://twitter.com/dzimine) on
Twitter, or as [Github issues](https://github.com/dzimine/serverless-
swarm/issues).


# Deploying Serverless Swarm, from 0 to 5.

Follow these step-by-step instructions to set up Docker Swarm, configure the rest of framework parts, and run a sample serverless pipeline.

## Clone the repo
This repo uses submodules, remember to use `recursive` when cloning:
```
git clone --recursive https://github.com/dzimine/serverless-swarm.git
cd serverless-swarm
```
If you have have already cloned the repo without `--recursive`, just do:
```
cd serverless-swarm
git submodule update --init --recursive
```
## Setting Up

All you need to get a swarm cluster running **conviniently**, per [Swarm
tutorial](https://docs.docker.com/engine/swarm/swarm-tutorial/).

### 1. Provision machines (with Vagrant)
First we need to provision machines where Swarm will be deployed. I'll use thee boxes:

| Host          | Role            |
|---------------|-----------------|
| st2.my.dev    | Swarm manager, Docker Registry, StackStorm     |
| node1.my.dev  | Swarm worker    |
| node2.my.dev  | Swarm worker    |

Roles are described as code in [`inventory.my.dev`]() file. Dah, this proto
setup is for play, not for production.


#### 1.1 Setup host machine
Vagrant is used to create a local dev environment representative of a production one, with convinience
tricks inspired by [6 practices for super smooth Ansible
experience](http://hakunin.com/six-ansible-practices). This will set 3 boxes,
named `st2.my.dev`, `node1.my.dev`, and `node2.my.dev`, with ssh access
configured for root.

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

#### 1.2 Vagrant up

Run `vagrant up`. You will need to type in the password to let Vagrant
update `/etc/hosts/`.

Profit! Log in as a root with `ssh st2.my.dev`, `ssh node1.my.dev`, and
`ssh node2.my.dev`. Check that the VMs' `/vagrant/` mount works: `ls /vagrant`.

Troubles: Due to [hostmanager bugs](https://github.com/devopsgroup-io/vagrant-
hostmanager/issues/159), `/etc/hosts` on the host machine may not be cleaned
up. Clean it up by hands.


### 2. Deploy Swarm cluster
Ok, machines are set up. Let deploy a 3-node Swarm cluster.
I use [ansible-dockerswarm](https://github.com/atosatto/ansible-dockerswarm) from
[@atosatto](https://github.com/atosatto) and my own addition to set up the local
Registry.

1. Create Swarm cluster:

    ```
    ansible-playbook playbook-swarm.yml -vv -i inventory.my.dev
    ```
2. Set up the [local Docker Registry](https://docs.docker.com/registry/deploying/)
    to host private docker images. 

    ```
    ansible-playbook playbook-registry.yml -vv -i inventory.my.dev
    ```
    Private registry is referred as `pregistry:5000`; it is set in
    `/etc/hosts` for consistency between Vagrant dev environment and AWS.
3. Add [Swarm visualizer](https://github.com/ManoMarks/docker-swarm-visualizer)
    for a nice eye-candy. Run this command on Swarm master.

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

    Wait for the service to start - here's a helper script:

    ```
    ./scripts/waitforservice.sh visualizer
    ```

    Connect to Visualizer via [http://st2.my.dev:8080](http://st2.my.dev:8080)
    and see this one server there.


### 3. Install StackStorm:

```sh
ansible-playbook playbook-st2.yml -vv -i inventory.my.dev

```

Install `pipeline` pack. A hackish way is to symlink it in place, for development:

```
ln -s /faas/pipeline/ /opt/stackstorm/packs/
st2 run packs.setup_virtualenv packs=pipeline
st2ctl reload
```

Check the action is in place: run `st2 action list --pack=pipeline` and verify
that it returned some actions.

**Pat yourself on a back, infra is done!** We got three nodes with docker,
running as Swarm, with local Registry, and StackStorm to rule them all.

### 4. Deploy on AWS with Terraform
Coming up...

## Play time!

Here comes a little refresher on how to run things on Swarm: with plain
Docker, with Swarm services, and with StackStorm actions and workflows. You
may want to skip it and jump right to [Wordcount Map-Reduce Example
](#wordcount-map-reduce-example).

### 1. Running an app, or "function", in plain Docker

The apps, or "functions" are placed in (drum-rolls...) `./functions`.
By the virtue of default Vagrant share, it is available inside
all VMs at `/vagrant/functions`.

Login to a VM. Any node would do as docker is installed on all.

    ssh node1.my.dev

1. Build a function:

    ```
    cd functions/encode
    docker build -t encode .
    ```
2. Push the function to local docker registry:

    ```
    docker tag encode pregistry:5000/encode
    docker push pregistry:5000/encode

    # Inspect the repository
    curl --cacert /etc/docker/certs.d/pregistry\:5000/registry.crt https://pregistry:5000/v2/_catalog
    curl --cacert /etc/docker/certs.d/pregistry\:5000/registry.crt -X GET https://pregistry:5000/v2/encode/tags/list
    ```
    >
    Note: Registry alias is set as `pregistry:5000` for brievity and consistency across Vagrand dev and AWS production environments.

4. Run the function:

    ```
    docker run --rm -v /share:/share \
    pregistry:5000/encode -i /share/li.txt -o /share/li.out --delay 1
    ```
    Reminders:

    * `--rm` to remove container once it exits.
    * `-v` maps `/share` of Vagrant VM to `/share` inside the container.
      This acts as a shared storage across Swarm VMs as `/share` maps to the host machine.
      On AWS we need to figure good shared storage alternative.
    * `-i`, `-o`, `--delay` are function parameters.


4. Login to another node, and run the container function from there. It will download the image and run the function.

### 2. Swarm is coming to town
Run the job with swarm command-line:

```
docker service create --name job2 \
--mount type=bind,source=/share,destination=/share \
--restart-condition none pregistry:5000/encode \
-i /share/li.txt -o /share/li.out --delay 20
```

Run it a few times, enjoy seeing them pile up in visualizer, just be sure to
give a different job name.

### 3. Now repeat with StackStorm

Run the job via stackstorm:

```
st2 run -a pipeline.run_job \
image=pregistry:5000/encode \
mounts='["type=bind,source=/share,target=/share"]' \
args="-i","/share/li.txt","-o","/share/test.out","--delay",3
```

To clean-up jobs (we've got a bunch!):

```
docker service rm $(docker service ls | grep "job*" | awk '{print $2}')
```

### 4. Stitch with Workflow
To run the workflow that executes multiple actions:

```
st2 run -a pipeline.pipe \
input_file=/share/li.txt output_file=/share/li.out \
parallels=4 delay=10
```
Use StackStorm UI at [https://st2.my.dev](https://st2.my.dev) to inspect workflow execution.


## Wordcount Map-Reduce Example

Here we run wordcount map-reduce sample on Swarm cluster. The `split`, `map`,
and `reduce` are containerized functions, `run_job` action runs them on Swarm
cluster, StackStorm workflow is orchestrating the end-to-end process.


Create containerized functions for map-reduce and push them to the Registry:

```
cd functions/wordcount
./docker-build.sh

```

Run the workflow:

```
st2 run -a pipeline.wordcount \
input_file=/share/loremipsum.txt result_filename=loremipsum.res \
parallels=8 delay=10
```

Enjoy the show via [Vizualizer at http://st2.my.dev:8080](http://st2.my.dev:8080)
and [StackStorm UI at https://st2.my.dev](https://st2.my.dev)

For details, see [functions/wordcount/README.md](functions/wordcount/README.md) and
inspect the code, docker containers, and pipeline workflow at
[pipeline/actions/wordcout.yaml](pipeline/actions/wordcout.yaml).

