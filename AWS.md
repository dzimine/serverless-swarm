# AWS Setup Guide


High level:

* Create manager and worker boxes, with terrafrom.
* Provision docker swarm, registry, stackstorm, and do wiring, with ansible
    * Check if all works
* Create auto-scaling group for worker nodes


### 1. Ready
1. Install Ansible and Terraform on a local machine.
2. Create AWS Route53 hosted zone, e.g. `example.net`.
3. Have AWS key pairs and access keys in place.
3. Put actual variables in `terraform/terraform.tfvars` (see `.example`).
4. Configure SSL on local machine for fun and profit:

    ```
    Host  *.example.net
    StrictHostKeyChecking no
    UserKnownHostsFile=/dev/null
    User root
    LogLevel ERROR
    ```
### 2. Go

1. From local machine, run Terraform - it will create two boxes with `DATA` and `share` storage under `/mnt`, `st2.example.net` and `node1.example.net`.

    ```
    cd terraform
    terraform apply -var 'instance_type_manager=t2.medium' -var 'instance_type_worker=t2.medium'
    ```

3. From local machine, run Ansible playbook to install Docker, enable Swarm, local Docker Registry, and StackStorm.

    ```
    ansible-playbook playbook-all.yml -vv -i inventory.aws
    ```

4. SSH to the st2.example box

    * Check that docker swarm is installed

        ```
        ssh st2.example.net
        docker node ls
        ```

    * Login visualizer to see that it's up: `http://st2.example.net:8080`

    * Check that share and data are mounted under /mnt on manager `st2.example.net` and worker `node1.example.net`.

5. Last mile configuration - now codified in `ansible-finaltouch`!

    * Check out `serverless-swarm` on `st2.example.net`:

        ```
        git clone https://github.com/dzimine/serverless-swarm.git /faas
        cd /faas
        ```
    * Install `pipeline` pack.

        ```
        ln -s /faas/pipeline/ /opt/stackstorm/packs/
        st2 run packs.setup_virtualenv packs=pipeline
        st2ctl reload
        ```
    > Note. This is temp hack, going forward functions are independent repositories, and run_job becomes part of standard swarm pack.
    * **On all boxes**, link `DATA` and `share`.
        ln -s /mnt/share/share /share
        ln -s /mnt/data/DATA /data

        TODO: Map /data and /share volume to Vagrant, too.

1. Run `wordcount` example.

    ```
    cd /faas/functions/wordcount
    ./docker-build.sh
    ```
    Ensure that it goes to the **right** repository (`pregistry:5000`)

    Run the action:

    ```
    st2 run -a pipeline.wordcount \
    input_file=/share/loremipsum.txt \
    result_filename=loremipsum.res \
    parallels=4 delay=30
    ```

2. Run `fgenesb` example.


    Add proprietary softberry components:

    ```
    cp -r /mnt/data/softberry/* /faas/functions/softberry
    ```

    Build docker images:

    ```
    cd /faas/functions/softberry/
    ./docker_build.sh
    ```

    Run the `findgenesb` worklfow:

    ```
    st2 run -a pipeline.findgenesb input_file=/share/test.seq \
    min_len=150 result_filename=result.result parallels=4
    ```







