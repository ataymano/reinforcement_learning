import multiprocessing
import logging
import sys

from helpers import vw, vw_opts, utils

def _safe_to_float(str, default):
    try:
        return float(str)
    except (ValueError, TypeError):
        return default

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

def _iteration(vw_path, cache, model_path_gen, commands, environment, job_pool):
    candidates = vw.train(vw_path, cache, model_path_gen, commands, job_pool)
    print('Local job is finished. Reducing...')
    candidates = environment.reduce(candidates)
    print('All candidates are reduced.')
    return _promote(candidates)

def sweep(vw_path, cache, model_path_gen, commands_lists, environment, job_pool, base_command = {}):
    result = [base_command]
    for idx, commands in enumerate(commands_lists):
        print('Iteration ' + str(idx))
        commands = environment.map(vw_opts.product(result, commands))
        result = _iteration(vw_path, cache, model_path_gen, commands, environment, job_pool)
    return result

if __name__ == '__main__':
    multiprocessing.freeze_support()
