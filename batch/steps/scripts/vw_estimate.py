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
parser.add_argument("--base_command", type=str, help="base command")
parser.add_argument("--marginals_index", type=str, help="marginal command index")
parser.add_argument("--interactions_index", type=str, help="interactions command index")

args = parser.parse_known_args()
metrics_folder = args[0].metrics_folder

os.makedirs(metrics_folder, exist_ok=True)

utils.logger("Input folder", args[0].input_folder)
utils.logger("Base command path", args[0].base_command)

with open(args[0].base_command, 'r') as f_command:
    command = f_command.readline()

marginals_path = os.path.join(args[0].input_folder, 'marginals.txt')
marg = ' '
if args[0].marginals_index:
    marg = get_subcommand(marginals_path, int(args[0].marginals_index))

inter = ' '
interactions_path = os.path.join(args[0].input_folder, 'interactions.txt')
if args[0].interactions_index:
    inter = get_subcommand(interactions_path, int(args[0].interactions_index))

if '-q' in command:
    tmpparser =  argparse.ArgumentParser("trtmpain")
    tmpparser.add_argument("-q", type=str, help="interactions command index")
    tmpargs = tmpparser.parse_known_args(command.split(' '))
    command = '--cb_adf --dsjson -q ' + tmpargs[0].q

c = command.rstrip() + ' ' +  ' '.join(args[1])

if marg is not None and inter is not None:
    c = c + ' ' + marg.rstrip() + ' ' + inter.rstrip()

    metadata_path = os.path.join(
        args[0].input_folder,
        'metadata.json'
    )

    with open(metadata_path) as json_file:
        metadata = json.load(json_file)

    previous_model = None
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
        print("sweep step cache path:")
        print(cache_file_path)

        command_options = {
            '--cache_file': cache_file_path,
        }

        if previous_model:
            previous_model_path = os.path.join(
                args[0].input_folder,
                previous_model
            )
            command_options['-i'] = previous_model_path

        command = vw.build_command(c, command_options)
        previous_model = date + '.vw'
        command_list.append(command)
        vw_output = vw.run(command)

    average_loss = vw.parse_average_loss(vw_output)

    metrics = {
        'command_list': command_list,
        'average_loss': average_loss
    }

    with open(metrics_path, 'w+') as fout:
        json.dump(metrics, fout)
