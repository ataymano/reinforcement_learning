import multiprocessing
import logging
import sys
from helpers import vw, vw_opts, utils

def safe_to_float(str, default):
    try:
        return float(str)
    except (ValueError, TypeError):
        return default

def simple(vw_path, cache, model_path_gen, commands, procs):
    candidates = vw.train(vw_path, cache, model_path_gen, commands, procs)
    bestLoss = sys.float_info.max
    bestCommand = None
    for c in candidates:
        utils.logger(vw_opts.serialize(c[0]), c[1])
        loss = safe_to_float(c[1], sys.float_info.max)
        if loss < bestLoss:
            bestLoss = loss
            bestCommand = c[0]
    return (bestCommand, bestLoss)

def multi(vw_path, cache, model_path_gen, commands_lists, procs):
    result = ({}, None)
    for commands in commands_lists:
        result = simple(vw_path, cache, model_path_gen, vw_opts.cartesian([result[0]], commands), procs)
    return result

if __name__ == '__main__':
    multiprocessing.freeze_support()
