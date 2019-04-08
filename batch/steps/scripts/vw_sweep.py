import argparse
import os
import glob
from helpers import vw, utils, grid_generator, path_generator, vw_opts, sweep, pool, environment

def vw_sweep(vw_path, input_folder, output, procs, env, models_path):
    model_path_gen = path_generator.folder_path_generator(models_path)
    pattern=os.path.join(input_folder, '*.cache')
    caches = list(glob.glob(pattern))
    base_command = {
        '#method':'--cb_adf',
        '#format':'--dsjson',
        '#saveresume':'--save_resume',
        '#savepercounters':'--preserve_performance_counters'}
    grid = grid_generator.generate()
    p = pool.multiproc_pool(procs) if procs > 1 else pool.seq_pool()
    env = environment.mpi() if env == 'mpi' else environment.local()
    result = sweep.sweep(vw_path, caches, model_path_gen, grid, env, p, base_command)
   
    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, 'w') as fout:
        for r in result:
            fout.write(vw_opts.serialize(r))

def main():
    print("Extracting data from application logs...")

    parser = argparse.ArgumentParser("create cache")
    parser.add_argument("--input_folder", type=str, help="input folder")
    parser.add_argument("--output", type=str, help="output")
    parser.add_argument("--vw", type=str, help="vw path")
    parser.add_argument("--procs", type=int, help="procs")
    parser.add_argument("--env", type=str, help="environment (local / mpi)")
    parser.add_argument("--models", type=str, help="models folder")
    args = parser.parse_args()

    utils.logger('Input folder', args.input_folder)
    utils.logger('Output', args.output)

    print('Sweeping...')
    vw_sweep(
        args.vw,
        args.input_folder,
        args.output,
        args.procs,
        args.env,
        args.models
    )
    print('Done.')


if __name__ == '__main__':
    main()
