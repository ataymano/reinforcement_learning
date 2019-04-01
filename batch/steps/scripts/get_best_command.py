# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.
import argparse
import os
import json
from azureml.core.run import Run


def Log(key, value):
        logger = Run.get_context()
        logger.log(key, value)
        print(key + ': ' + str(value))


def to_float(str):
    try:
        return float(str)
    except ValueError:
        return None


def get_best_command(path, metrics):
    with open(path, 'r') as f:
        o = json.loads(f.read())
        best = None
        for el in o:
            if metrics in o[el].keys():
                m = to_float(o[el][metrics][0])
            else:
                m = None
            if m is not None and (best is None or m < best[1]):
                best = (o[el]['Command'][0], m)

    if best is None:
        raise ValueError('Best variant was not selected')

    return best


print("Selecting best command...")

parser = argparse.ArgumentParser("select_best_command")
parser.add_argument("--input", type=str, help="input metrics")
parser.add_argument("--output", type=str, help="output")
args = parser.parse_args()

Log("Input metrics", args.input)
Log("Output path", args.output)

metrics_name = 'average loss'
best = get_best_command(args.input, metrics_name)

Log('Command', best[0])
Log(metrics_name, best[1])

os.makedirs(os.path.dirname(args.output), exist_ok=True)
with open(args.output, 'w+') as fout:
    fout.write(best[0] + '\n')
    fout.write(str(best[1]))
print('Done.')
