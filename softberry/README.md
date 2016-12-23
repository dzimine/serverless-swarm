Prepare:

From the root `./` folder

* Put data in `./DATA`
* Put software in `./softberry`

Build container:

```
# get on build node
ssh node1.my.dev

# Build docker container
cd /vagrant/softberry
docker build -t fb . 

```

Create a `share` dir and copy sequence file there:

```
mkdir ./share
cp softberry/test.sec share
```

Run conatiner:

```
docker run -it -v /vagrant/DATA:/sb/DATA -v /vagrant/share:/share  --rm fb /share/test.seq /share/test.res 150
```

Pick up results in `share`
