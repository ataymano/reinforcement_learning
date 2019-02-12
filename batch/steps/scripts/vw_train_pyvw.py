# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.
import argparse
import os
from vowpalwabbit import pyvw

class vw_wrapper:
    def __init__(self, vw_path, args):
        self._vw = pyvw.vw(args)

    def parse_vw_output(self, txt):
        result = {}
        for line in txt.split('\n'):
            if '=' in line:
                index = line.find('=')
                key = line[0:index].strip()
                value = line[index+1:].strip()
                result[key] = value
        return result

    def process(self, input, output):
        with open(input) as f:
            for line in f:
                try:
                    self._vw.learn(line)
                except:
                    print('Cannot process line: ' + line)
        self._vw.save(output)
        return 1

print("In train.py")
print("As a data scientist, this is where I use my training code.")

parser = argparse.ArgumentParser("train")
parser.add_argument("--input_folder", type=str, help="input folder")
parser.add_argument("--output_folder", type=str, help="output folder")
args = parser.parse_args()

print("Argument 1: %s" % args.input_folder)
print("Argument 2: %s" % args.output_folder)

print("CREATING VW WRAPPER:")
vw = vw_wrapper(vw_path = '/usr/local/bin/vw', args = '--cb_adf --dsjson')
print("DONE")

os.makedirs(args.output_folder, exist_ok=True)
result = vw.process(os.path.join(args.input_folder, '0.json'), os.path.join(args.output_folder, 'current'))
print('RESULT: ' +  result)


