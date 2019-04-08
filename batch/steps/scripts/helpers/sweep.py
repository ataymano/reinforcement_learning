import multiprocessing
import logging
import sys
from helpers import vw, vw_opts, utils

def _safe_to_float(str, default):
    try:
        return float(str)
    except (ValueError, TypeError):
        return default

def _aggregate(candidates):
    return candidates

def _promote(candidates):
    bestLoss = sys.float_info.max
    bestCommand = None
    for c in candidates:
        utils.logger(vw_opts.serialize(c[0]), c[1])
        loss = _safe_to_float(c[1], sys.float_info.max)
        if loss < bestLoss:
            bestLoss = loss
            bestCommand = c[0]
    return [bestCommand]

def _iteration(vw_path, cache, model_path_gen, commands, job_pool):
    candidates = vw.train(vw_path, cache, model_path_gen, commands, job_pool)
    return _promote(_aggregate(candidates))

def sweep(vw_path, cache, model_path_gen, commands_lists, job_pool, base_command = {}):
    result = [base_command]
    for commands in commands_lists:
        result = _iteration(vw_path, cache, model_path_gen, vw_opts.product(result, commands), job_pool)
    return result

if __name__ == '__main__':
    multiprocessing.freeze_support()
