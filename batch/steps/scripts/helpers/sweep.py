import multiprocessing
import logging
import sys

from helpers import vw, vw_opts, logger

def _safe_to_float(str, default):
    try:
        return float(str)
    except (ValueError, TypeError):
        return default

def _promote(candidates, env):
    bestLoss = sys.float_info.max
    bestCommand = None
    for c in candidates:
        env.logger.log_scalar_global(vw_opts.to_commandline(c[0]), c[1])
        loss = _safe_to_float(c[1], sys.float_info.max)
        if loss < bestLoss:
            bestLoss = loss
            bestCommand = c[0]
    return [bestCommand]

def _iteration(vw_path, cache, model_path_gen, commands, env):
    candidates = vw.train(vw_path, cache, model_path_gen, commands, env)
    env.logger.trace('Local job is finished. Reducing...')
    candidates = env.runtime.reduce(candidates)
    env.logger.trace('All candidates are reduced.')
    return _promote(candidates, env)

def sweep(vw_path, cache, model_path_gen, commands_lists, env, base_command = {}):
    result = [base_command]
    for idx, commands in enumerate(commands_lists):
        env.logger.trace('Iteration ' + str(idx))
        commands = env.runtime.map(vw_opts.product(result, commands))
        result = _iteration(vw_path, cache, model_path_gen, commands, env)
    return result

if __name__ == '__main__':
    multiprocessing.freeze_support()
