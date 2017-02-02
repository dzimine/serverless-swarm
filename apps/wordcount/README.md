# Word count map-reduce in Python.

A toy map-reduce app that counts words occurence in a file.
Consists of `split.py`, `map.py`, and `reduce.py`.


### Usage

On a small file.
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
wordcount/split.py data/loremipsum.txt 2 data/out
for i in 1 2; do wordcount/map.py data/out.$i data/out.map.$i ; done
ls data
cat data/out.map.* > data/map.out
wordcount/reduce.py data/map.out data/loremipsum.res
cat data/loremipsum.res
rm data/*out*
```

## Development
To run unit tests, install `pytest` and run it from project root.
