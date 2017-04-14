# AWS Setup Guide


High level, the idea is:

* Create manager and worker boxes, with terrafrom.
* Provision docker swarm, registry, stackstorm, and do wiring, with ansible.
* Create auto-scaling group for worker nodes


### 1. Ready
1. Install Ansible and Terraform on a local machine.
3. Have AWS key pairs and access keys in place.
3. Put actual variables in `terraform/terraform.tfvars` (see `.example`).
2. Create AWS Route53 hosted zone, e.g. `example.net`. Put it in terraform/variables.tf
3. Review other variables in [`terraform/variables.tf`](terraform/variables.tf),
   create nessessary resources, and put their IDs as variables.
4. Configure SSL on local machine for fun and profit:

    ```
    Host  *.example.net
    StrictHostKeyChecking no
    UserKnownHostsFile=/dev/null
    User root
    LogLevel ERROR
    ```

### 2. Go

1. From local machine, run Terraform.

    ```
    cd terraform
    terraform apply -var 'instance_type_manager=t2.medium' -var 'instance_type_worker=t2.medium' -var 'n_workers=2'
    ```

    This will do quite a few things:

    1. Creates boxes with `data` and `share` storage mounted under `/mnt`.
    2. Create DNS records for `st2.example.net`, `node1.example.net`, etc.
    3. Run ansible to provision Docker, Swarm, and Stackstorm exactly like on Vagrant.
       At this point we have an enviromnent identical to local dev.
    4. Create an auto-scaling group, using a snapshot of `node1.example.net`worker
       an AMI, so that all is already provisioned for fast hot-create.
       When auto-scaling group scales out, worker nodes automatically join the Swarm.

### 3. Play

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
