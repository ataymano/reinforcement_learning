# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.
import argparse
import os
import json

def get_label_cost(parsed):
    if 'o' in parsed:
        reward = 0
        for o in parsed['o']:
            if 'v' in o:
                return -o['v']
    return 0

def get_chosen_a_p(parsed):
    return (parsed['a'][0], parsed['p'][0]) 

def add_label(line):
    parsed = json.loads(line)
    _label_cost = get_label_cost(parsed)
    chosen_a_p = get_chosen_a_p(parsed)
    _label_probability = chosen_a_p[1]
    _label_Action = chosen_a_p[0]
    _labelIndex = _label_Action - 1

    return '{"_label_cost":'+str(_label_cost) + ',"_label_probability":' \
        + str(_label_probability) + ',"_label_Action":' + str(_label_Action) \
        + ',"_labelIndex":' + str(_labelIndex) + ',' + line[1:]

def add_label_if_required(line):
    if (line.startswith('{"_label_cost')):
        return line
    return add_label(line)

def add_labels(input_file, output_file):
    with open(output_file, 'w') as fout:
        with open(input_file, 'r') as fin:
            for line in fin:
                fout.write(add_label_if_required(line))

print("Adding training labels...")

parser = argparse.ArgumentParser("add_label")
parser.add_argument("--input_folder", type=str, help="input folder")
parser.add_argument("--output_folder", type=str, help="output folder")
args = parser.parse_args()

print("Argument 1: %s" % args.input_folder)
print("Argument 2: %s" % args.output_folder)

os.makedirs(args.output_folder, exist_ok=True)

input = os.path.join(args.input_folder, 'dataset.json')
output = os.path.join(args.output_folder, 'dataset.json')
add_labels(input, output)
print("Done.")
