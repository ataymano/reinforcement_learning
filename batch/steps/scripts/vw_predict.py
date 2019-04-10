# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.
import argparse
import os
import argparse
import os
import glob
from helpers import vw, logger, grid, path_generator, vw_opts, pool, environment, runtime

def predict(vw_path, cache_folder, output_folder, commands_file, model_folder, procs):
    pattern=os.path.join(cache_folder, '*.cache')
    cache_list = sorted(list(glob.glob(pattern)))
    predict_opts = {'#method': '--cb_explore_adf --epsilon 0.2'}
    commands = list(map(lambda lo: vw_opts.labeled(lo.name, vw_opts.apply(lo.opts, predict_opts)),
                       map(lambda l : vw_opts.labeled.deserialize(l), open(commands_file, 'r').readlines())))
    env = environment.environment(
        vw_path = vw_path,
        runtime = runtime.local(),
        job_pool = pool.multiproc_pool(procs) if procs > 1 else pool.seq_pool(),
        model_path_gen = path_generator.model_path_generator(model_folder),
        pred_path_gen = path_generator.pred_path_generator(output_folder)
        )
    env.logger.log_scalar_global('Cache folder', cache_folder)
    env.logger.log_scalar_global('Output folder', output_folder)
    env.logger.log_scalar_global('Commands', commands_file)

    vw.predict(cache_list, commands, env)

def main():
    parser = argparse.ArgumentParser("predict")
    parser.add_argument("--cache_folder", type=str, help="cache folder")
    parser.add_argument("--model_folder", type=str, help="model folder")
    parser.add_argument("--commands", type=str, help="commands")
    parser.add_argument("--output_folder", type=str, help="output_folder")
    parser.add_argument("--vw", type=str, help="vw path")
    parser.add_argument("--procs", type=int, help="procs")


    args = parser.parse_args()
    predict(args.vw, args.cache_folder, args.output_folder, args.commands, args.model_folder, args.procs)

if __name__ == '__main__':
    main()
