## Running genomic pipeline with containers

Softberry scripts and binaries are used in this pipeline. To reproduce, get `softberry.tar.gz` from [TBD]().

The following containers are built:

* `blast` - basic (TODO: use opensource blast from dockerhub)
* `sb_base` - base Softberry image
* `fgenesb` - encapsulates FgenesB - finding genes and bacterias
* `blast_fb` - runs blast computations (on multiple nodes)
* `fgenesb_out` - processes (reduces) blast results and produces filan output.

#### Build the containers

1. Prepare. Exctract softberry.tar.gz.
    * Put data in `./DATA`
    * Put software in `./softberry`

2. Build containers and push them to local Registry:

    ```
    # get on build node
    ssh node1.my.dev

    # Build docker containers
    /vagrant/softberry/docker-build.sh
    ```
3. Create a `share` dir and copy the sequence file there:

    ```
    mkdir ./share
    cp softberry/test.seq share
    ```


### Run the pipeline manually

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

### Run StackStorm workflow
Put the sequence input file (e.g. `test.seq`) in `share` and launch workflow action:

```
st2 run pipeline.findgenesb input_file=/share/test.seq min_len=150 result_file=/share/result.result parallels=4
```