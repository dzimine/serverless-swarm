1. Prepare:

From the root `./` folder

* Put data in `./DATA`
* Put software in `./softberry`

2. Build container:

```
# get on build node
ssh node1.my.dev

# Build docker container
cd /vagrant/softberry
docker build -t fb .

```

3. Create a `share` dir and copy sequence file there:

```
mkdir ./share
cp softberry/test.sec share
```

4. Run conatiner:

```
docker run -it -v /vagrant/DATA:/sb/DATA -v /vagrant/share:/share  --rm fb /share/test.seq /share/test.res 150
```

5. Pick up results in `share`
