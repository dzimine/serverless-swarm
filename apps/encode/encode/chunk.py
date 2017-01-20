#!/usr/bin/env python
import os
import sys


def readline_chunk(filename, chunk, chunks):
    """
    Generator to read lines from chunk of file.

    Args:
        filename(string): name/path to file
        chunk(int>0): which chunk the lines are read from (out of `chunks`)
        chunks(int>0): how manu chunks file is broken to
    """
    size = os.stat(filename).st_size
    start_pos = int(((chunk - 1) * size) / chunks)
    end_pos = size if chunk == chunks else int((chunk * size) / chunks)
    f = open(filename, 'r')
    f.seek(start_pos)
    if chunk > 1:
        f.readline()

    while True:
        if f.tell() > end_pos:
            break
        line = f.readline().rstrip()
        if not line:
            break
        yield line
    f.close


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Usage %s FILE CHUNK CHUNKS" % sys.argv[0]
        exit(1)
    filename = sys.argv[1]
    chunk = int(sys.argv[2])
    chunks = int(sys.argv[3])

    lines = chars = 0
    for line in readline_chunk(filename, chunk, chunks):
        print line
        lines += 1
        chars += len(line)
    print "Read {} lines {} characters.".format(lines, chars)
