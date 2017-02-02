#!/usr/bin/env python
import sys

import wordcount

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "REDUCE: Consolidates results for word count."
        print "Usage: %s INPUT_FILE OUTPUT_FILE" % sys.argv[0]
        exit(1)

    in_fn = sys.argv[1]
    out_fn = sys.argv[2]

    with open(in_fn, 'r') as in_file, open(out_fn, 'w') as out_file:
        for word, count in wordcount.words_reduce_stream(in_file):
            out_file.write("{} {}\n".format(word, count))
