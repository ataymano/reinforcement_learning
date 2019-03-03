# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.
import argparse
import os
from azureml.core.run import Run
def Log(key, value):
        logger = Run.get_context()
        logger.log(key, value)
        print(key + ': ' + str(value))

print("Preparing command...")

parser = argparse.ArgumentParser("prepare_command")
parser.add_argument("--command_output", type=str, help="output folder")
args = parser.parse_known_args()


Log("Output path", args[0].command_output)
command = ' '.join(args[1])
Log("Command", command)
os.makedirs(os.path.dirname(args[0].command_output), exist_ok=True)
with open(args[0].command_output, 'w+') as fout:
    fout.write(command)
print('Done.')


