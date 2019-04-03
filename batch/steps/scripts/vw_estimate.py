# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.
import json
import argparse
import os
from helpers import vw
from helpers import utils
import uuid


def get_subcommand(fname, index):
    if index == 0:
        return ' '
    if os.path.isfile(fname):
        with open(fname, 'r') as f:
            for result in f:
                index = index - 1
                if index == 0:
                    return result
    return None

print("Estimating vw model...")

parser = argparse.ArgumentParser("sweep")
parser.add_argument("--input_folder", type=str, help="input folder")
parser.add_argument("--metrics_folder", type=str, help="metrics folder")
parser.add_argument("--model_folder", type=str, help="model folder")
parser.add_argument("--base_command", type=str, help="base command")
parser.add_argument("--previous_policy", type=str, help="previous policy")
parser.add_argument("--marginals_index", type=str, help="marginal command index")
parser.add_argument("--interactions_index", type=str, help="interactions command index")

args = parser.parse_known_args()
metrics_folder = args[0].metrics_folder
model_folder = args[0].model_folder
base_command = args[0].base_command
previous_policy = args[0].previous_policy

os.makedirs(metrics_folder, exist_ok=True)
os.makedirs(model_folder, exist_ok=True)

utils.logger("Input folder", args[0].input_folder)
print("base command:")
print(base_command)
print(previous_policy)

if previous_policy:
    best_command_path = os.path.join(
        base_command,
        previous_policy + '_command'
    )
else:
    best_command_path = base_command

utils.logger("Base command path:", best_command_path)

with open(best_command_path, 'r') as f_command:
    command = f_command.readline()
    # if previous_policy == 'Quad':
    #     q_index = command.find(' -q ')
    #     marginal_index = command.find(' --marginal ')
    #     quad_index = 0
    #     if (q_index > -1 and marginal_index > -1):
    #         quad_index = min(q_index, marginal_index)
    #     elif (q_index > -1):
    #         quad_index = q_index
    #     else:
    #         quad_index = marginal_index
    #     command = command[q_index:]
marginals_path = os.path.join(args[0].input_folder, 'marginals.txt')
marg = ' '
if args[0].marginals_index:
    marg = get_subcommand(marginals_path, int(args[0].marginals_index))

inter = ' '
interactions_path = os.path.join(args[0].input_folder, 'interactions.txt')
if args[0].interactions_index:
    inter = get_subcommand(interactions_path, int(args[0].interactions_index))

if '-q' in command:
    print('-q in command')
    print(command)
    tmpparser =  argparse.ArgumentParser("trtmpain")
    tmpparser.add_argument("-q", type=str, help="interactions command index")
    tmpargs = tmpparser.parse_known_args(command.split(' '))
    command = '--cb_adf --dsjson -q ' + tmpargs[0].q

print("==args[1]==")
print(args[1])
c = command.rstrip() + ' ' +  ' '.join(args[1])
if marg and inter:
    c = c + ' ' + marg.rstrip() + ' ' + inter.rstrip()
print("c: " + c)

metadata_path = os.path.join(
    args[0].input_folder,
    'metadata.json'
)

with open(metadata_path) as json_file:
    metadata = json.load(json_file)

previous_model_path = None
vw_output = None
command_list = []
metrics_path = os.path.join(
    metrics_folder,
    str(uuid.uuid4()) + '.json'
)

for date in metadata.get('date_list'):
    cache_file_path = os.path.join(
        args[0].input_folder,
        date + '.cache'
    )
    new_model_path = os.path.join(
        model_folder,
        date + '.vw'
    )
    command_options = {
        '--cache_file': cache_file_path,
        '-f': new_model_path
    }

    if previous_model_path:
        command_options['-i'] = previous_model_path

    command = vw.build_command(c, command_options)
    previous_model_path = new_model_path

    vw_output = vw.run(command)
    print("command: " + command)
    print(vw_output)
    print("*********************************")
average_loss = vw.parse_average_loss(vw_output)

metrics = {
    "command": c,
    "average_loss": average_loss
}

with open(metrics_path, 'w+') as fout:
    json.dump(metrics, fout)
