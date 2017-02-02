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

    with open(filename, 'r') as f:
        f.seek(start_pos)
        if chunk > 1:
            f.readline()
        while True:
            if f.tell() > end_pos:
                break
            line = f.readline()
            if not line:
                break
            yield line

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Splits file to N near-equal chunks, respecting EOL."
        print "Usage %s FILE CHUNKS OUTPUT_FILE_PREFIX" % sys.argv[0]
        exit(1)

    filename = sys.argv[1]
    chunks = int(sys.argv[2])
    output_file_prefix = sys.argv[3]

    for chunk in range(1, chunks + 1):
        output_fn = "{}.{}".format(output_file_prefix, chunk)
        lines_total = chars_total = 0
        with open(output_fn, 'w') as of:
            print "Writing to file {}...".format(output_fn)
            lines = chars = 0
            for line in readline_chunk(filename, chunk, chunks):
                print line.rstrip()
                of.write(line)
                lines += 1
                chars += len(line)
            of.write('\n')
            print "Wrote {} lines {} characters to {}".format(lines, chars, output_fn)
            lines_total += lines
            chars_total += chars
        print "Total {} lines {} characteres.".format(lines_total, chars_total)
