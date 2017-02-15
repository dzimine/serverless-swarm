## Running genomic pipeline with containers



### Get Softberry
Softberry scripts and binaries are used in this pipeline. Download `softberry.tar.gz` from a secret location [^1]. Exctract `softberry.tar.gz`.

* Put data in `../DATA` 
* Put software in `./softberry` (this directory)


[^1]: Softberry software contains trade-secret algorithms and kept proprietary. If you
  have the rights to it, you should have a key to a secret location. For the rest,
  please play with other examples.


### Build the containers
Containers can be build on any docker node, with access to code. Ssh there, go to `softberry`, and run the script to build the containers.

    ```
    # get on a build node
    ssh st2.my.dev

    # Build docker containers
    /vagrant/softberry/docker-build.sh
    ```
The following containers are built:

* `blast` - basic (TODO: use opensource blast from dockerhub)
* `sb_base` - base Softberry image
* `fgenesb` - encapsulates FgenesB - finding genes and bacterias
* `blast_fb` - runs blast computations (on multiple nodes)
* `fgenesb_out` - processes (reduces) blast results and produces filan output.

### Run pipeline as a StackStorm workflow
SSH to a controller node (`st2.my.dev`). Place the sequence input file (e.g. `test.seq`) in the `share`, and launch workflow action:

```
st2 run -a pipeline.findgenesb input_file=/vagrant/share/test.seq \
min_len=150 result_filename=result1.result parallels=4
```

### How to run the pipeline manually

1. Run `fgenesb` conatiner:

    ```
    docker run -it -v /vagrant/DATA:/sb/DATA -v /vagrant/share:/share  --rm \
    st2.my.dev:5000/fgenesb /share/test.seq /share/test.res 150
    ```

   Check results in `share`.

2. Prepare data for blast run, assuming 2 parallel blast executors:

    ```
    docker run -it --rm -v /vagrant/DATA:/sb/DATA -v /vagrant/share:/share st2.my.dev:5000/sb_base

    /sb/blast_scripts/fgenesb_get_proteins.pl /share/test.res > /share/prot2blast.0

    /sb/extra/seqsplit.py /share/prot2blast.0 /share/out 2
    ```

3. Run BLAST (2 times, for 2 parts):

    ```
    docker run -it --rm -v /vagrant/DATA:/sb/DATA -v /vagrant/share:/share \
    st2.my.dev:5000/blast_fb /share/out.1 /sb/DATA/cog_db/cog.pro \
    /share/out.1.1 /sb/blast-2.2.26/bin/blastpgp 1e-10  4

    docker run -it --rm -v /vagrant/DATA:/sb/DATA -v /vagrant/share:/share \
    st2.my.dev:5000/blast_fb /share/out.2 /sb/DATA/cog_db/cog.pro \
    /share/out.1.2 /sb/blast-2.2.26/bin/blastpgp 1e-10  4
    ```

4. Locally on the host (any with access to `share`), combine blast results by concating the files:

    ```
    cat  /vagrant/share/out.1.* > /vagrant/share/fin_prot
    ```

5. Build final result
    ```
    docker run -it --rm -v /vagrant/DATA:/sb/DATA -v /vagrant/share:/share \
    st2.my.dev:5000/fgenesb_out /share/test.res /share/fin_prot /share/final_result
    ```
