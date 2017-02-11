# Word count map-reduce in Python. Dockerized!

A toy map-reduce app that counts words occurence in a file.
Consists of `split.py`, `map.py`, and `reduce.py`.


### Usage

Test on a tiny file:

```
wordcount/map.py data/nory.txt data/out.txt && \
wordcount/reduce.py data/out.txt data/res.txt && \
cat data/res.txt

a 6
catholic 6
was 6
because 3
her 3
mother 3
and 2
father 2
nory 1
been 1
his 1
norys 1
or 1
had 1

```

Now splitting by 2 and reducing back:

```
# Split a file by two
wordcount/split.py data/loremipsum.txt 2 data/out
# Map two parts
for i in 1 2; do wordcount/map.py data/out.$i data/out.map.$i ; done
# Check what we got
ls data
# Combine map output together
cat data/out.map.* > data/map.out
# Reduce to results
wordcount/reduce.py data/map.out data/loremipsum.res
cat data/loremipsum.res
rm data/*out*
```

## Running in docker

Ssh to the any of a docker boxes, e.g. `ssh st2.my.dev`. Move (It is `/vagrant/` in dev environment, adjust accordingly).

Build docker containers:

```
cd cd /vagrant/apps/wordcount/

docker build -t split -f Split.Dockerfile .
docker build -t map -f Map.Dockerfile .
docker build -t reduce -f Reduce.Dockerfile .
```

Manually run the map-reduce with containerized functions:

```
# Split intput file by 2 chunks
docker run -it -v /vagrant/share/:/share split /share/loremipsum.txt 2 /share/out
# Run map on the two chunks
for i in 1 2; do docker run -it -v /vagrant/share:/share map /share/out.$i /share/map.out.$i; done
# Combine map output in one file
cat /vagrant/share/map.out.* > /vagrant/share/map.out
# Reduce to results
docker run -it -v /vagrant/share:/share reduce /share/map.out /share/loremipsum.res
# See the answer:
cat /vagrant/share/loremipsum.res
# Check that it's correct
diff /vagrant/share/loremipsum.res /vagrant/apps/wordcount/data/loremipsum.res
# Clean up intermediate files
rm /vagrant/share/*out*

 ```

## Orchestrate with StackStorm workflow

```
st2 run -a pipeline.wordcount \
input_file=/vagrant/share/loremipsum.txt result_filename=loremipsum.res \
parallels=8 delay=10
```

## Unit tests
Install `pytest` and run it from project root.
