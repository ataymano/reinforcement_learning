# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.
import argparse
import os
import json
import sys
from helpers import utils


print("Selecting best command...")

parser = argparse.ArgumentParser("select_best_command")
parser.add_argument("--metrics_folder", type=str, help="metrics folder")
parser.add_argument("--best_commands_folder", type=str, help="output")
parser.add_argument("--policy_name", type=str, help="policy name")

args = parser.parse_args()
metrics_folder = args.metrics_folder
best_commands_folder = args.best_commands_folder
policy_name = args.policy_name

utils.logger("Metrics folder", metrics_folder)
utils.logger("Best commands folder", best_commands_folder)

os.makedirs(best_commands_folder, exist_ok=True)

best_command = None
min_average_loss = sys.float_info.max

for metrics_file in os.listdir(metrics_folder):
    metrics_path = os.path.join(metrics_folder, metrics_file)
    with open(metrics_path) as json_file:
        metrics = json.load(json_file)
        print(metrics)
        if (float(metrics.get('average_loss')) < min_average_loss):
            best_command = metrics.get('command')

best_command_path = os.path.join(
    best_commands_folder,
    policy_name + '_command'
)

with open(best_command_path, 'w+') as fout:
    fout.write(best_command)
