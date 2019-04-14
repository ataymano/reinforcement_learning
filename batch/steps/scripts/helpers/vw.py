import subprocess
import logging
import os
import datetime
import time
import sys

from helpers import vw_opts, logger

def _safe_to_float(str, default):
    try:
        return float(str)
    except (ValueError, TypeError):
        return default

def _cache(input, opts, env):
    opts['-d'] = input
    opts['--cache_file'] = env.cache_path_gen.get(input)
    return (opts, run(build_command(env.vw_path, opts), env.logger))

def _cache_func(input):
    return _cache(input[0], input[1], input[2])

def _cache_multi(opts, env):
    input_files = env.txt_provider.get()
    inputs = list(map(lambda i: (i, opts, env), input_files))
    result = env.job_pool.map(_cache_func, inputs)
    return result

def _train(cache_file, opts, env):
    opts['--cache_file'] = cache_file
    opts['-f'] = env.model_path_gen.get(cache_file, opts)
    start = time.time()
    result = (opts, run(build_command(env.vw_path, opts), env.logger))
    end = time.time()
    env.logger.log_scalar_local('[Perf] ' + os.path.basename(cache_file), float(end - start))
    return result

def _train_func(input):
    return _train(input[0], input[1], input[2])

def _train_multi(opts, env):
    previous = [(None, None)] * len(opts)
    cache_files = env.cache_provider.get()
    for c in cache_files:
        inputs = list(map(lambda o: (c, o, env), opts))
        result = env.job_pool.map(_train_func, inputs)
        opts = list(map(lambda r: r[0], result))
        for o in opts:
            o['-i'] = o['-f']
    return result

def _predict(cache_file, labeled_opts, env):
    labeled_opts.opts['-p'] = env.pred_path_gen.get(cache_file, labeled_opts.name)
    result = _train(cache_file, labeled_opts.opts, env)
    return (vw_opts.labeled(labeled_opts.name, result[0]), result[1])

def _predict_func(input):
    return _predict(input[0], input[1], input[2])

def _predict_multi(labeled_opts, env):
    previous = [(None, None)] * len(labeled_opts) 
    cache_files = env.cache_provider.get()
    for c in cache_files:
        inputs = list(map(lambda lo: (c, lo, env), labeled_opts))
        result = env.job_pool.map(_predict_func, inputs)
        opts = list(map(lambda r: r[0], result))
        for o in opts:
            o.opts['-i'] = o.opts['-f']
    return result

def _parse_vw_output(txt):
    result = {}
    for line in txt.split('\n'):
        if '=' in line:
            index = line.find('=')
            key = line[0:index].strip()
            value = line[index+1:].strip()
            result[key] = value
    return result

def run(command, logger):
    logger.trace('Running: ' + command)
    start = time.time()
    process = subprocess.Popen(
        command.split(),
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    output, error = process.communicate()
    end = time.time()
    logger.trace('Done: ' + command)
    return _parse_vw_output(error)

def build_command(path, opts={}):
    return ' '.join([path, vw_opts.to_commandline(opts)])

def build_command_legacy(vw_path, command='', opts={}):
    if command:
        command = ' '.join([
            vw_path,
            command,
            '--save_resume',
            '--preserve_performance_counters'
        ])
    else:
        command = ' '.join([
            vw_path,
            '--cb_adf',
            '--dsjson',
            '--save_resume',
            '--preserve_performance_counters'
        ])

    for key, val in opts.items():
        command = ' '.join([
            command,
            key,
            str(val)
        ])
    return command

def cache(opts, env):
    result = _cache_multi(opts, env)
    opts.pop('--cache_file', None)
    opts.pop('-d', None)

def train(opts, env):
    if not isinstance(opts, list):
        opts = [opts]

    result = _train_multi(opts, env)
    for r in result:
        r[0].pop('-f', None)
        r[0].pop('-i', None)
        r[0].pop('--cache_file', None)
    return list(map(lambda r: (r[0], _safe_to_float(r[1]['average loss'], sys.float_info.max)), result))

def predict(labeled_opts, env):
    if not isinstance(labeled_opts, list):
        labeled_opts = [labeled_opts]

    _predict_multi(labeled_opts, env)

if __name__ == '__main__':
    multiprocessing.freeze_support()

