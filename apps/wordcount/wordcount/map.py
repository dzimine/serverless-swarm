#!/usr/bin/env python
import sys

import wordcount

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Counts word occurance in a file"
        print "Usage %s INPUT_FILE OUTUPT_FILE" % sys.argv[0]
        exit(1)

    in_fn = sys.argv[1]
    out_fn = sys.argv[2]

    with open(in_fn, 'r') as in_file, open(out_fn, 'w') as out_file:
        for line in in_file:
            for word, count in wordcount.words_in_text(line):
                out_file.write("{} {}\n".format(word, count))
