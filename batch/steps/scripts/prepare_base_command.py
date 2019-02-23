# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.
import argparse
import os

print("Preparing base command...")

parser = argparse.ArgumentParser("prepare_base_command")
parser.add_argument("--base_command_output", type=str, help="output folder")
args = parser.parse_known_args()

print("Output path: %s" % args[0].base_command_output)

os.makedirs(os.path.dirname(args[0].base_command_output), exist_ok=True)
with open(args[0].base_command_output, 'w+') as fout:
    fout.writelines([' '.join(args[1])])
print('Done.')


