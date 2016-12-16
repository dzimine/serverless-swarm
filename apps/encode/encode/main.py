import argparse
import base64
import json
import os
import time

def transform(data):
    return base64.b64encode(data)

def parse_args():

    parser = argparse.ArgumentParser(description='Toy data transformer')

    parser.add_argument('-i', '--input',  dest='inp', required=True, help="Input data file")
    parser.add_argument('-o', '--output', dest="out", required=True, help="Output data file")
    parser.add_argument('--delay', dest="delay", type=int, default=0, help="Delay, seconds")

    args = parser.parse_args()
    return (args.inp, args.out, args.delay)

if __name__ == '__main__':

    (source_fn, dest_fn, delay) = parse_args()
    
    with open(source_fn) as sf:
        r = transform(sf.read())
        with open(dest_fn, "w") as df:
            df.write(r)

    time.sleep(delay)
    print json.dumps({
                'output_file': dest_fn,
                'output_path': os.path.abspath(dest_fn),
                'delay': delay,
            }, indent=4,)



