#!/usr/bin/env python
import sys
import time

import wordcount

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "\nMAP: Counts word occurance in a file"
        print "Usage %s INPUT_FILE OUTUPT_FILE [DELAY]" % sys.argv[0]
        exit(1)

    in_fn = sys.argv[1]
    out_fn = sys.argv[2]
    delay = 0 if len(sys.argv) < 4 else int(sys.argv[3])

    with open(in_fn, 'r') as in_file, open(out_fn, 'w') as out_file:
        for line in in_file:
            for word, count in wordcount.words_in_text(line):
                out_file.write("{} {}\n".format(word, count))
    time.sleep(delay)
