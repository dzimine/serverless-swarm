## How to prepare containers

`softberry` is used to build . Get `softberry.tar.gz` from TBD.

The following containers are built:

* `blast` - basic (TODO: use opensource blast from dockerhub)
* `sb_base` - base Softberry image
* `fgenesb` - encapsulates FgenesB - finding genes and bacterias
* `blast_prep` - prepares to run blust in parallels on multiple nodes
* `blast_fb` - runs blast computations (on multiple nodes)
* `fgenesb_out` - processes (reduces) blast results and produces filan output.

To build the containers:

1. Prepare. From the root `./` folder
    * Put data in `./DATA`
    * Put software in `./softberry`

2. Build containers:

    ```
    # get on build node
    ssh node1.my.dev

    # Build docker containers
    /vagrant/softberry/docker-build.sh

    # Push the conatiners to the local registry
    docker images | grep st2.my.dev | awk '{ system("docker push " $1) }'

    ```
3. Create a `share` dir and copy the sequence file there:

    ```
    mkdir ./share
    cp softberry/test.seq share
    ```

4. Run `fgenesb` conatiner:

    ```
    docker run -it -v /vagrant/DATA:/sb/DATA -v /vagrant/share:/share  --rm \
    st2.my.dev:5000/fgenesb /share/test.seq /share/test.res 150
    ```

5. Pick up results in `share`


### More
Prepare the blast data:
```
docker run -it -v /vagrant/DATA:/sb/DATA -v /vagrant/share:/share st2.my.dev:5000/sb_base

/sb/blast_scripts/fgenesb_get_proteins.pl /share/test.res > /share/prot2blast.0 

/sb/extra/seqsplit.py /share/prot2blast.0 /share/out 2
```

Run BLAST (manually, split by two, for manual example):

```
# 
docker run -it --rm -v /vagrant/DATA:/sb/DATA -v /vagrant/share:/share st2.my.dev:5000/blast_fb /share/out.1 /sb/DATA/cog_db/cog.pro /share/out.1.1 /sb/blast-2.2.26/bin/blastpgp 1e-10  4

docker run -it --rm -v /vagrant/DATA:/sb/DATA -v /vagrant/share:/share st2.my.dev:5000/blast_fb /share/out.2 /sb/DATA/cog_db/cog.pro /share/out.1.2 /sb/blast-2.2.26/bin/blastpgp 1e-10  4

Locally on the host, concat files:
```

cat  /vagrant/share/out.1.* > /vagrant/share/fin_prot
```

Build final result
```
docker run -it --rm -v /vagrant/DATA:/sb/DATA -v /vagrant/share:/share st2.my.dev:5000/fgenesb_out /share/test.res /share/fin_prot /share/final_result
```

